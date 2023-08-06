# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
This file contains utilty functions for Training
"""
import os
import json
import argparse
from math import isnan
from typing import Optional, Dict, Any

import torch
from datasets.arrow_dataset import Dataset
from transformers import TrainingArguments, Seq2SeqTrainingArguments, Seq2SeqTrainer
from transformers.trainer import Trainer, TRAINING_ARGS_NAME
from transformers.trainer_callback import TrainerCallback
from transformers.trainer_utils import IntervalStrategy

from optimum.onnxruntime import ORTTrainer, ORTSeq2SeqTrainer

from ..constants import HfTrainerMethodsConstants, HfTrainerType, AzuremlRunType
from .logging_utils import get_logger_app


logger = get_logger_app()


class TrainerMixin:
    """
    This is a mixin class that needs to used in conjunction with either of the below classes
        Trainer
        ORTTrainer
        Seq2SeqTrainer
        ORTSeq2SeqTrainer
    This class provides extra utility functions for trainer. Also it helps to customize some methods.
    """

    CUSTOM_FUNCTIONS = {}

    def _save(self, output_dir: str, state_dict=None):
        # NOTE updating the state dict for mmaction onboarding
        self.model.save_pretrained(output_dir, state_dict=self.model.state_dict())
        if self.tokenizer:
            self.tokenizer.save_pretrained(output_dir)
        torch.save(self.args, os.path.join(output_dir, TRAINING_ARGS_NAME))

    def load_model_finetuned_weights(self, resume_from_checkpoint: str):
        """
        load finetuned weights of a model
        applies lora weights + deepspeed init is handled internally
        """
        self.state.best_model_checkpoint = resume_from_checkpoint
        self._load_best_model()
        self.state.best_model_checkpoint = None

    def _get_train_sampler(self) -> Optional[torch.utils.data.Sampler]:
        if HfTrainerMethodsConstants.AZUREML_TRAIN_SAMPLER in self.__class__.CUSTOM_FUNCTIONS:
            custom_train_sampler_func = self.__class__.CUSTOM_FUNCTIONS[HfTrainerMethodsConstants.AZUREML_TRAIN_SAMPLER]
            logger.info(f"Using custom train sampler: {custom_train_sampler_func}")
            return custom_train_sampler_func(self.train_dataset, self.args.world_size)
        else:
            logger.info("Calling the default train sampler")
            return super()._get_train_sampler()

    def _get_eval_sampler(self, eval_dataset: Dataset) -> Optional[torch.utils.data.Sampler]:
        if HfTrainerMethodsConstants.AZUREML_EVAL_SAMPLER in self.__class__.CUSTOM_FUNCTIONS:
            custom_eval_sampler_func = self.__class__.CUSTOM_FUNCTIONS[HfTrainerMethodsConstants.AZUREML_EVAL_SAMPLER]
            logger.info(f"Using custom eval sampler: {custom_eval_sampler_func}")
            return custom_eval_sampler_func(eval_dataset, self.args.world_size)
        else:
            logger.info("Calling the default eval sampler")
            return super()._get_eval_sampler(eval_dataset)

    def create_optimizer(self):
        if HfTrainerMethodsConstants.AZUREML_OPTIMIZER in self.__class__.CUSTOM_FUNCTIONS:
            create_optimizer_func = self.__class__.CUSTOM_FUNCTIONS[HfTrainerMethodsConstants.AZUREML_OPTIMIZER]
            logger.info(f"Using custom optimizer: {create_optimizer_func}")
            self.optimizer = create_optimizer_func(self.model, learning_rate=self.args.learning_rate)
        else:
            logger.info("Calling the default optimizer")
            super().create_optimizer()

    def compute_loss(self, model, inputs, return_outputs=False):
        if HfTrainerMethodsConstants.AZUREML_COMPUTE_LOSS in self.__class__.CUSTOM_FUNCTIONS:
            compute_loss_func = self.__class__.CUSTOM_FUNCTIONS[HfTrainerMethodsConstants.AZUREML_COMPUTE_LOSS]
            logger.info(f"Using custom loss func: {compute_loss_func}")
            return compute_loss_func(model, inputs, return_outputs=return_outputs)
        else:
            return super().compute_loss(model, inputs, return_outputs=return_outputs)


class TrainerExtended(TrainerMixin, Trainer):
    """
    Subclassed Trainer class to customize behaviour
    """
    pass

    # CUSTOM_FUNCTIONS = {}

    # def _save(self, output_dir: str, state_dict=None):
    #     # NOTE updating the state dict for mmaction onboarding
    #     self.model.save_pretrained(output_dir, state_dict=self.model.state_dict())
    #     if self.tokenizer:
    #         self.tokenizer.save_pretrained(output_dir)
    #     torch.save(self.args, os.path.join(output_dir, TRAINING_ARGS_NAME))

    # def load_model_finetuned_weights(self, resume_from_checkpoint: str):
    #     """
    #     load finetuned weights of a model
    #     applies lora weights + deepspeed init is handled internally
    #     """
    #     self.state.best_model_checkpoint = resume_from_checkpoint
    #     self._load_best_model()
    #     self.state.best_model_checkpoint = None

    # def _get_train_sampler(self) -> Optional[torch.utils.data.Sampler]:
    #     if HfTrainerMethodsConstants.AzmlTrainSampler in TrainerExtended.CUSTOM_FUNCTIONS:
    #         custom_train_sampler_func = TrainerExtended.CUSTOM_FUNCTIONS[HfTrainerMethodsConstants.AzmlTrainSampler]
    #         logger.info(f"Using custom train sampler: {custom_train_sampler_func}")
    #         return custom_train_sampler_func(self.train_dataset, self.args.world_size)
    #     else:
    #         logger.info("Calling the default train sampler")
    #         return super()._get_train_sampler()

    # def _get_eval_sampler(self, eval_dataset: Dataset) -> Optional[torch.utils.data.Sampler]:
    #     if HfTrainerMethodsConstants.AzmlEvalSampler in TrainerExtended.CUSTOM_FUNCTIONS:
    #         custom_eval_sampler_func = TrainerExtended.CUSTOM_FUNCTIONS[HfTrainerMethodsConstants.AzmlEvalSampler]
    #         logger.info(f"Using custom eval sampler: {custom_eval_sampler_func}")
    #         return custom_eval_sampler_func(eval_dataset, self.args.world_size)
    #     else:
    #         logger.info("Calling the default eval sampler")
    #         return super()._get_eval_sampler(eval_dataset)

    # def create_optimizer(self):
    #     if HfTrainerMethodsConstants.AzmlOptimizer in TrainerExtended.CUSTOM_FUNCTIONS:
    #         create_optimizer_func = TrainerExtended.CUSTOM_FUNCTIONS[HfTrainerMethodsConstants.AzmlOptimizer]
    #         logger.info(f"Using custom optimizer: {create_optimizer_func}")
    #         self.optimizer = create_optimizer_func(self.model, learning_rate=self.args.learning_rate)
    #     else:
    #         logger.info("Calling the default optimizer")
    #         super().create_optimizer()

    # def compute_loss(self, model, inputs, return_outputs=False):
    #     if HfTrainerMethodsConstants.AzmlComputeLoss in TrainerExtended.CUSTOM_FUNCTIONS:
    #         compute_loss_func = TrainerExtended.CUSTOM_FUNCTIONS[HfTrainerMethodsConstants.AzmlComputeLoss]
    #         logger.info(f"Using custom loss func: {compute_loss_func}")
    #         return compute_loss_func(model, inputs, return_outputs=return_outputs)
    #     else:
    #         return super().compute_loss(model, inputs, return_outputs=return_outputs)


class Seq2SeqTrainerExtended(TrainerMixin, Seq2SeqTrainer):
    """
    Subclassed Trainer class to customize behaviour
    """
    pass


class ORTTrainerExtended(TrainerMixin, ORTTrainer):
    """
    Subclassed Trainer class to customize behaviour. ORT is assumed to be pre-installed in the PTCA image
    """
    pass


class ORTSeq2SeqTrainerExtended(TrainerMixin, ORTSeq2SeqTrainer):
    """
    Subclassed Trainer class to customize behaviour
    """
    pass


def identify_trainer_cls(trainer_type: str, apply_ort: bool):
    """
    Identify the trainer class and training arguments class
    """
    if trainer_type == HfTrainerType.SEQ2SEQ:
        return ORTSeq2SeqTrainerExtended if apply_ort else Seq2SeqTrainerExtended
    else:
        return ORTTrainerExtended if apply_ort else TrainerExtended


def identify_training_args_cls(trainer_type: str):
    """
    Identify the trainer class and training arguments class
    """
    if trainer_type == HfTrainerType.SEQ2SEQ:
        return Seq2SeqTrainingArguments
    return TrainingArguments


# Trainer call back to log metrics
# TODO move to mlflow logging
class FinetuneCallback(TrainerCallback):
    """
    A [`TrainerCallback`] that sends the logs to [AzureML](https://pypi.org/project/azureml-sdk/).
    """

    def __init__(self, azureml_run=None, log_metrics_at_root=True, set_log_prefix=True):
        """
        init azureml_run which is azureml Run object
        """
        self.azureml_run = azureml_run
        self.log_metrics_at_root = log_metrics_at_root
        self.set_log_prefix = set_log_prefix

    def _should_log_to_parent(self):
        """
        Check if we should log to parent pipeline run.

        :return: Parent run if we should log else None.
        :rtype: azureml.core.run
        """
        parent_run = self.azureml_run.parent
        child_run = None
        while parent_run is not None and (parent_run.type == AzuremlRunType.PIPELINE_RUN or parent_run.type == AzuremlRunType.STEP_RUN):
            child_run = parent_run
            parent_run = parent_run.parent
        return child_run

    def on_init_end(self, args, state, control, **kwargs):
        """
        executes after init and sets azureml_run
        """
        from azureml.core.run import Run

        if self.azureml_run is None and state.is_world_process_zero:
            self.azureml_run = Run.get_context()
            logger.info("Initialized azureml run")

        if self.azureml_run is not None and "OfflineRun" in self.azureml_run.id:
            logger.info("Failed to get context, run as Local run")
            self.azureml_run = None

    def on_log(self, args, state, control, logs=None, **kwargs):
        """
        logs metrics to azureml
        """
        if self.azureml_run and state.is_world_process_zero:
            steps = None
            if args.logging_strategy == IntervalStrategy.STEPS:
                steps = state.global_step
            for k, v in logs.items():
                if isinstance(v, (int, float)) and not isnan(v):
                    
                    if not self.set_log_prefix:
                        eval_prefix = 'eval_'
                        train_prefix = 'train_'
                        if k.startswith(eval_prefix):
                            k = k[len(eval_prefix):]
                        if k.startswith(train_prefix):
                            k = k[len(train_prefix):]
                            k = k + '_train'

                    self.azureml_run.log(k, v, description=k, step=steps)

                    if self.log_metrics_at_root:
                        # Check if parent is a pipeline run.
                        # If pipeline run, log all metrics to parent pipeline as well.
                        parent_run = self._should_log_to_parent()
                        if parent_run:
                            logger.info(f"Logging metrics to {parent_run}")
                            parent_run.log(k, v, description=k, step=steps)
        else:
            logger.info(f"Logging metrics for local run with step {state.global_step} - {logs}")


def resolve_conflicts_trainer_deepspeed_args(finetune_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    :param finetune_args: finetune component args loaded from component parameters
        If deepspeed is enabled, read the deepspeed config args and resolve conflicts with trainer_args
        NOTE deepspeed config parameters are given preference over component parameters
    """

    finetune_args_namespace = argparse.Namespace(**finetune_args)

    if finetune_args_namespace.deepspeed is not None:
        with open(finetune_args_namespace.deepspeed) as fp:
            ds_dict = json.load(fp)

        # per_device_train_batch_size
        # deepspeed - train_batch_size can not be handled currently, needs to be checked by user only
        # TODO: replicate for eval batch size
        if hasattr(finetune_args_namespace, "per_device_train_batch_size"):
            per_device_train_batch_size = ds_dict.get("train_micro_batch_size_per_gpu", finetune_args_namespace.per_device_train_batch_size)
            if per_device_train_batch_size != "auto":
                setattr(finetune_args_namespace, "per_device_train_batch_size", per_device_train_batch_size)

        # gradient_accumulation_steps
        if hasattr(finetune_args_namespace, "gradient_accumulation_steps"):
            gradient_accumulation_steps = ds_dict.get("gradient_accumulation_steps", finetune_args_namespace.gradient_accumulation_steps)
            if gradient_accumulation_steps != "auto":
                setattr(finetune_args_namespace, "gradient_accumulation_steps", gradient_accumulation_steps)

        # train_batch_size - not implemented as calculated by HFTrainer

        # max_grad_norm
        if hasattr(finetune_args_namespace, "max_grad_norm"):
            max_grad_norm = ds_dict.get("gradient_clipping", finetune_args_namespace.max_grad_norm)
            if max_grad_norm != "auto":
                setattr(finetune_args_namespace, "max_grad_norm", max_grad_norm)

        # optimizer
        if "optimizer" in ds_dict and "params" in ds_dict["optimizer"]:
            # learning_rate
            if hasattr(finetune_args_namespace, "learning_rate"):
                learning_rate = ds_dict["optimizer"]["params"].get("lr", finetune_args_namespace.learning_rate)
                if learning_rate != "auto":
                    setattr(finetune_args_namespace, "learning_rate", learning_rate)
            # adam_betas
            if hasattr(finetune_args_namespace, "adam_beta1") and hasattr(finetune_args_namespace, "adam_beta2"):
                if "betas" in ds_dict["optimizer"]["params"] and ds_dict["optimizer"]["params"]["betas"] != "auto":
                    setattr(finetune_args_namespace, "adam_beta1", ds_dict["optimizer"]["params"]["betas"][0])
                    setattr(finetune_args_namespace, "adam_beta2", ds_dict["optimizer"]["params"]["betas"][1])
            # adam_epsilon
            if hasattr(finetune_args_namespace, "adam_epsilon"):
                adam_epsilon = ds_dict["optimizer"]["params"].get("eps", finetune_args_namespace.adam_epsilon)
                if adam_epsilon != "auto":
                    setattr(finetune_args_namespace, "adam_epsilon", adam_epsilon)
            # weight_decay
            if hasattr(finetune_args_namespace, "weight_decay"):
                weight_decay = ds_dict["optimizer"]["params"].get("weight_decay", finetune_args_namespace.weight_decay)
                if weight_decay != "auto":
                    setattr(finetune_args_namespace, "weight_decay", weight_decay)

        # scheduler
        if "scheduler" in ds_dict and "params" in ds_dict["scheduler"]:
            # learning_rate
            if hasattr(finetune_args_namespace, "learning_rate"):
                learning_rate = ds_dict["scheduler"]["params"].get("warmup_max_lr", finetune_args_namespace.learning_rate)
                if learning_rate != "auto":
                    setattr(finetune_args_namespace, "learning_rate", learning_rate)
            # warmup_steps
            if hasattr(finetune_args_namespace, "warmup_steps"):
                warmup_steps = ds_dict["scheduler"]["params"].get("warmup_num_steps", finetune_args_namespace.warmup_steps)
                if warmup_steps != "auto":
                    setattr(finetune_args_namespace, "warmup_steps", warmup_steps)
            # max_steps
            if hasattr(finetune_args_namespace, "max_steps"):
                max_steps = ds_dict["scheduler"]["params"].get("total_num_steps", finetune_args_namespace.max_steps)
                if max_steps != "auto":
                    setattr(finetune_args_namespace, "max_steps", max_steps)

        # fp-16
        if hasattr(finetune_args_namespace, "fp16"):
            fp16 = ds_dict.get("fp16", {}).get("enabled", finetune_args_namespace.fp16)
            if fp16 != "auto":
                setattr(finetune_args_namespace, "fp16", fp16)
        # fp16_full_eval, fp16_backend - not implemented by azmlft
        # fp16_backend is auto handled by HfTrainerDeepSpeedConfig and is always "amp" for azmlft
        setattr(finetune_args_namespace, "fp16_opt_level", "O1")      # default HFTrainer value
        fp16_opt_level = ds_dict.get("amp", {}).get("opt_level", finetune_args_namespace.fp16_opt_level)
        if fp16_opt_level != "auto":
            setattr(finetune_args_namespace, "fp16_opt_level", fp16_opt_level)

        # bf-16
        # bf16 - not implemented by azmlft
        setattr(finetune_args_namespace, "bf16", False)           # default HFTrainer value
        bf16 = ds_dict.get("bf16", {}).get("enabled", finetune_args_namespace.bf16)
        if bf16 != "auto":
            setattr(finetune_args_namespace, "bf16", bf16)
        
        logger.info(f"Resolved conflicts between finetune_args_namespace and deepspeed config: {finetune_args_namespace}")

    else:
        setattr(finetune_args_namespace, "fp16_opt_level","O1")  # default HFTrainer value
        setattr(finetune_args_namespace, "bf16", False)          # default HFTrainer value

    return vars(finetune_args_namespace)
