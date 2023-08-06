# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Error strings for custom errors
"""


class LLMErrorStrings:
    """
    Class defining custom error strings
    """

    LLM_GENERIC_ERROR = "An error occurred [{error}]"
    TASK_NOT_SUPPORTED = "Given Task [{TaskName}] is not supported, Please check name or supply different task"
    MODEL_NOT_SUPPORTED = "Given Model [{ModelName}] is not supported, Please check name or provide different model"
    MODEL_INCOMPATIBLE_WITH_TASK = (
        "The selected Model [{ModelName}] doesn't support the current Task [{TaskName}], "
        "Please select a different model")
    TOKENIZER_NOT_SUPPORTED = (
        "The selected Tokenizer [{Tokenizer}] doesn't support the current Task [{TaskName}], "
        "Please select a different tokenizer or tokenizer type")
    VALIDATION_ERROR = "Error while validating parameters [{error}]"
    RESOURCE_NOT_FOUND = "Resource [{ResourceName}] not found"
    INVALID_CHECKPOINT_DIRECTORY = "Provide a valid checkpoint directory. Got [{dir}]"
    PATH_NOT_FOUND = "Path [{path}] was not found"
    ML_CLIENT_NOT_CREATED = (
        "Failed to create ML Client. This is likely            because you didn't create a managed identity           "
        " and assign it to your compute cluster."
    )
    DEPLOYMENT_FAILED = "Failed to create deployment with error [{error}]"
    PREDICTION_FAILED = "Prediction Failed with error [{error}]"
    INVALID_LABEL = "Label {label} is not found in training/validation data"
    INVALID_DATASET = "Only one label found in training and validation data combined"
