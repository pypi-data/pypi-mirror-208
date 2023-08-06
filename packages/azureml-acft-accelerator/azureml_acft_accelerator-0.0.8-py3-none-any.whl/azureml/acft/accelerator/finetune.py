# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
File Containing Functions for finetuning a pre trained model
"""

import os
import json
import time
import math
from dataclasses import asdict
from typing import Any, Callable, Dict, List, Union, Optional
from pathlib import Path
import shutil

from transformers import TrainerCallback
from transformers import PreTrainedTokenizerBase, PreTrainedModel
from transformers.trainer import Trainer
from transformers.trainer_seq2seq import Seq2SeqTrainer
from transformers.trainer_callback import EarlyStoppingCallback
from transformers.trainer_utils import IntervalStrategy

import torch
import torch.nn as nn
import torch.distributed as dist
from torch.utils.data import Dataset as TorchDataset, IterableDataset as TorchIterableDataset

from datasets.arrow_dataset import Dataset as DatasetsDataset
from datasets.iterable_dataset import IterableDataset as DatasetsIterableDataset

from .constants import SaveFileConstants, MetricConstants, AzuremlConstants
from .constants import _AzuremlOptimizationArgs, _AzuremlIOArgs, HfTrainerType
from .utils.logging_utils import get_logger_app
from .utils.hf_argparser import HfArgumentParser
from .utils.license_utils import download_license_file

from .utils.trainer_utils import (
    identify_training_args_cls,
    identify_trainer_cls,
    resolve_conflicts_trainer_deepspeed_args,
    FinetuneCallback
)
from .utils.decorators import swallow_all_exceptions
from .utils.model_utils import (
    print_model_summary,
    add_lora_layers_to_model
)


logger = get_logger_app()


class AzuremlFinetuneArgs:
    def __init__(
        self,
        finetune_args: Dict[str, Any],
        trainer_type: str = HfTrainerType.DEFAULT,
    ) -> None:

        # resolve deepspeed vs trainer parameters
        if finetune_args.get("deepspeed", None) is not None:
            finetune_args = resolve_conflicts_trainer_deepspeed_args(finetune_args)

        if trainer_type not in HfTrainerType.get_fields():
            raise Exception(f"Trainer type not supported. It should be one of {HfTrainerType.get_fields()}")
        self.trainer_type = trainer_type

        training_args_cls = identify_training_args_cls(trainer_type)
        logger.info(f"Identified training args class: {training_args_cls}")

        # Set this flag to enable training in CPU computes
        if not torch.cuda.is_available():
            finetune_args["xpu_backend"] = "mpi"
            finetune_args["no_cuda"] = True
            logger.warning(
                "CPU compute based training is in experimental stage. ONLY single process training works for now"
            )

        # parse the data into training args and optimzation args
        parser = HfArgumentParser([_AzuremlOptimizationArgs, _AzuremlIOArgs, training_args_cls])
        (self.optimization_args, self.io_args, self.trainer_args), unsed_args = parser.parse_dict(
            finetune_args, allow_extra_keys=True)
        logger.info(f"Optimization args: {self.optimization_args}")
        logger.info(f"IO args: {self.io_args}")
        logger.info(f"The following args are unused by the trainer - {unsed_args}")

        self.__post_init__()
        logger.info(f"Trainer args: {self.trainer_args}")

    def __post_init__(self):
        """Set some additional trainer args"""
        setattr(self.trainer_args, "report_to", [])
        # Loads the model at the end of training so that the best model will be saved in the end
        setattr(self.trainer_args, "load_best_model_at_end", True)

    def save(self):
        if self.trainer_args.should_save:  # save only on rank-0
            # saving only optimization and io args here
            # trainer args will be save as part of :func trainer _save method
            optimization_args_save_path = os.path.join(self.io_args.pytorch_model_folder, SaveFileConstants.OPTIMIZATION_ARGS_SAVE_PATH)
            with open(optimization_args_save_path, 'w') as fp:
                json.dump(asdict(self.optimization_args), fp, indent=2)

            io_args_save_path = os.path.join(self.io_args.pytorch_model_folder, SaveFileConstants.IO_ARGS_SAVE_PATH)
            with open(io_args_save_path, 'w') as fp:
                json.dump(asdict(self.io_args), fp, indent=2)


class AzuremlDatasetArgs:
    def __init__(
        self,
        train_dataset: Union[TorchDataset, TorchIterableDataset, DatasetsDataset, DatasetsIterableDataset],
        validation_dataset: Union[TorchDataset, TorchIterableDataset, DatasetsDataset, DatasetsIterableDataset],
        data_collator: Optional[Callable],
    ):
        self.train_dataset = train_dataset
        self.validation_dataset = validation_dataset
        self.data_collator = data_collator


class AzuremlTrainer:
    """Azureml trainer class to train/finetune the model"""

    def __init__(
        self,
        finetune_args: AzuremlFinetuneArgs,
        dataset_args: AzuremlDatasetArgs,
        model: Union[nn.Module, PreTrainedModel],
        tokenizer: Optional[PreTrainedTokenizerBase]=None,
        metric_func: Optional[Callable]=None,
        custom_trainer_callbacks: Optional[List[TrainerCallback]]=None,
        custom_trainer_functions: Optional[Dict[str, Callable]]=None,
        new_initalized_layers: Optional[List[str]]=None,
        hf_trainer: Optional[Union[Trainer, Seq2SeqTrainer]]=None
    ):
        self.finetune_args = finetune_args
        self.optimization_args = finetune_args.optimization_args
        self.io_args = finetune_args.io_args
        self.trainer_args = finetune_args.trainer_args
        self.trainer_cls = identify_trainer_cls(finetune_args.trainer_type, self.optimization_args.apply_ort)
        logger.info(f"Identified trainer class: {self.trainer_cls}")

        self.dataset_args = dataset_args
        self.custom_trainer_functions = custom_trainer_functions or {}
        self.custom_trainer_callbacks = custom_trainer_callbacks or []

        # TODO add validations for interfaces
        self.model = model
        self.new_initalized_layers = new_initalized_layers
        self.tokenizer = tokenizer
        self.metric_func = metric_func

        self.__post_init__()

    def __post_init__(self):
        # TODO add validations for interfaces
        # set attributes to the trainer function
        setattr(self.trainer_cls, "CUSTOM_FUNCTIONS", self.custom_trainer_functions)

    @swallow_all_exceptions(logger)
    def train(self):
        """
        prepares necessary objects for finetuning and triggers finetuning and saves the best model
        """

        model, lora_wrapper_obj = self.model, None
        is_lora_weights_path_exist = False
        if self.optimization_args.model_name is not None:
            finetune_lora_weights_path = os.path.join(
                self.io_args.model_selector_output, self.optimization_args.model_name, \
                    AzuremlConstants.LORA_BASE_FOLDER, AzuremlConstants.LORA_WEIGHTS_NAME)
            is_lora_weights_path_exist = os.path.isfile(finetune_lora_weights_path)
        if self.optimization_args.apply_lora:
            model, lora_wrapper_obj = add_lora_layers_to_model(
                model=model,
                unmerge_weights=is_lora_weights_path_exist,
                optimizer_args=self.optimization_args,
                new_initialized_layers=self.new_initalized_layers
            )

        print_model_summary(model, print_params=True)

        # resetting eval_steps only for fixed size datasets
        if (
            isinstance(self.dataset_args.train_dataset, (DatasetsDataset, TorchDataset)) and
            self.trainer_args.evaluation_strategy == IntervalStrategy.STEPS and self.optimization_args.evaluation_steps_interval > 0
        ):
            logger.info("Updating eval steps")
            # TODO Move this to post_init
            num_examples = len(self.dataset_args.train_dataset)  # type:ignore
            logger.info(f"number of trining examples: {num_examples}, world size: {self.trainer_args.world_size}")
            num_update_steps_per_epoch = num_examples // self.trainer_args.gradient_accumulation_steps
            num_update_steps_per_epoch = max(num_update_steps_per_epoch, 1)
            num_update_steps_per_epoch_per_world = max(num_update_steps_per_epoch // self.trainer_args.world_size, 1)
            mod_steps = int(math.floor(num_update_steps_per_epoch_per_world * self.optimization_args.evaluation_steps_interval))
            setattr(self.trainer_args, "eval_steps", mod_steps)
            setattr(self.trainer_args, "save_steps", mod_steps)
            # TODO Update evaluation_steps in scripts file to eval_steps
            logger.info(f"Updated evaluation_steps from {self.trainer_args.eval_steps} to {mod_steps}")

        # adding trainer callbacks
        trainer_callbacks = []
        trainer_callbacks.append(
            FinetuneCallback(log_metrics_at_root=self.optimization_args.log_metrics_at_root,
                             set_log_prefix=self.optimization_args.set_log_prefix)
        )
        if self.optimization_args.apply_early_stopping:
            logger.info("Applying Early stopping as trainer callback")
            early_stopping = EarlyStoppingCallback(
                early_stopping_patience=self.optimization_args.early_stopping_patience,
                early_stopping_threshold=self.optimization_args.early_stopping_threshold,
            )
            trainer_callbacks.append(early_stopping)
        # Add the additional trainbacks supplied by the user
        trainer_callbacks.extend(self.custom_trainer_callbacks)
        logger.info(trainer_callbacks)

        self.hf_trainer = self.ft_with_trainer(model, trainer_callbacks=trainer_callbacks, load_lora_weights=is_lora_weights_path_exist)

        # Saving the model (TODO move the saving of mlflow and lora based merge to trainer utils)
        # no lora
        #   - only base model (HF model) weights will be saved to pytorch_model.bin
        # lora
        #   - merge_lora_weights=True
        #       - base weights will be saved to pytorch_model.bin
        #       - lora weights will be saved to `AzuremlConstants.LoraBaseFolder`/pytorch_model.bin
        logger.info(f"Saving the fine-tuned model to {self.io_args.pytorch_model_folder}")
        # merging the lora layers on process 0
        if lora_wrapper_obj is not None and self.hf_trainer.args.should_save and self.optimization_args.apply_lora:
            lora_layer_search_strings = AzuremlConstants.LORA_LAYER_SEARCH_STRINGS
            logger.info(f"Merging the lora weights! Lora layer search strings: {lora_layer_search_strings}")

            self.hf_trainer.model = lora_wrapper_obj.merge_lora_layers(
                self.hf_trainer.model, lora_layer_search_strings=lora_layer_search_strings)

            # store the lora layers state dict separately
            lora_layers_state_dict = lora_wrapper_obj.get_lora_layers_state_dict(
                self.hf_trainer.model, lora_layer_search_strings=lora_layer_search_strings)
            lora_weights_save_path = os.path.join(
                self.io_args.pytorch_model_folder, AzuremlConstants.LORA_BASE_FOLDER, AzuremlConstants.LORA_WEIGHTS_NAME)
            os.makedirs(os.path.dirname(lora_weights_save_path), exist_ok=True)
            logger.info(f"Saving the lora weights to {lora_weights_save_path}")
            torch.save(lora_layers_state_dict, lora_weights_save_path)  # save only lora weights

            # set the ignore weights to lora layers so that only HF model weights will be saved
            # TODO see if there is a way to not set the private variable
            ignore_keys = list(lora_layers_state_dict.keys())
            # TODO keys_to_ignore_on_save is not valid for nn.Module
            self.hf_trainer.model._keys_to_ignore_on_save = ignore_keys
            logger.info(f"Ignoring the following keys while saving the merged lora model: {ignore_keys}")

        # In Trainer, model save happens only in main process
        # https://huggingface.co/docs/transformers/main_classes/trainer#transformers.Trainer.save_model
        self.hf_trainer.save_model(self.io_args.pytorch_model_folder)

        # saving input model LICENSE file to output
        # TODO need to handle LICENSE file as part of model import compnent or contrib package
        if self.hf_trainer.args.should_save and self.optimization_args.model_name:
            license_file_path = Path(self.io_args.model_selector_output, \
                                self.optimization_args.model_name, SaveFileConstants.LICENSE_SAVE_PATH)
            if license_file_path.is_file():
                shutil.copy(str(license_file_path), self.io_args.pytorch_model_folder)
                logger.info("LICENSE file is copied to pytorch model folder")
            else:
                download_license_file(self.optimization_args.model_name, self.io_args.pytorch_model_folder)

        # saving the args
        self.finetune_args.save()

        # Adding a barrier to wait for all the processes to finish
        if dist.is_initialized():
            logger.info("Waiting at barrier")
            dist.barrier()

    def ft_with_trainer(
        self,
        model: Union[nn.Module, PreTrainedModel],
        trainer_callbacks: List[TrainerCallback],
        load_lora_weights: bool = False
    ) -> Trainer:
        """
        handles the finetuning of a pre-trained model
        """

        if dist.is_initialized():
            logger.info(f"local_rank = {dist.get_rank()}; world_size = {dist.get_world_size()}")
        else:
            logger.info("dist is not initialized")

        logger.info(self.trainer_args)
        trainer = self.trainer_cls(
            model=model,
            train_dataset=self.dataset_args.train_dataset,  # type: ignore
            eval_dataset=self.dataset_args.validation_dataset,  # type: ignore
            compute_metrics=self.metric_func,
            args=self.trainer_args,
            tokenizer=self.tokenizer,
            data_collator=self.dataset_args.data_collator,
            callbacks=trainer_callbacks,
        )

        logger.info("Training started!")
        start_time = time.time()
        # Continual Finetuning case
        if load_lora_weights and self.optimization_args.model_name:
            # load the lora weights for the case where model is saved using merge_lora_weights=True
            lora_weights_folder = os.path.join(self.io_args.model_selector_output, \
                                               self.optimization_args.model_name, AzuremlConstants.LORA_BASE_FOLDER)
            logger.info(f"Loading the lora weights from {lora_weights_folder}")
            trainer.load_model_finetuned_weights(resume_from_checkpoint=lora_weights_folder)
        trainer.train()
        end_time = time.time()
        logger.info("Training completed in {} sec".format(end_time - start_time))

        return trainer

    @property
    def should_save(self):
        return self.hf_trainer.args.should_save
