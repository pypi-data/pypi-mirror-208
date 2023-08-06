# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
This file defines the decorators used in the package
"""

import time
from email import message
from inspect import trace
import logging
from functools import wraps
import functools
import traceback
from azureml._common.exceptions import AzureMLException
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore
from .error_handling.error_definitions import LLMInternalError, ValidationError
from .error_handling.exceptions import ValidationException
from .config import Config


def swallow_all_exceptions(logger: logging.Logger):
    """
    Swallow all exceptions
    1. Catch all the exceptions arising in the functions wherever used
    2. Raise the exception as an AzureML Exception so that it does not get scrubbed by PII scrubber
    :param logger: The logger to be used for logging the exception raised
    :type logger: Instance of logging.logger
    """

    def wrap(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValidationException as e:
                az_e = AzureMLException._with_error(AzureMLError.create(ValidationError, error=e))

                logger.error("Exception {} when calling {}".format(az_e, func.__name__))
                logger.info("exiting due to validation error")

                for handler in logger.handlers:
                    handler.flush()

                raise AzureMLException._with_error(AzureMLError.create(ValidationError, error=e))
            except Exception as e:
                # This will be logged to exceptions table
                az_e = AzureMLException._with_error(AzureMLError.create(LLMInternalError, error=e))

                logger.error("Exception {} when calling {}".format(az_e, func.__name__))
                logger.info("exiting due to system error")

                for handler in logger.handlers:
                    handler.flush()

                raise AzureMLException._with_error(AzureMLError.create(LLMInternalError, error=e))

        return wrapper

    return wrap


def retry(times, logger):
    """
    Retry Decorator
    Retries the wrapped function/method `times` times if the exceptions listed
    in ``exceptions`` are thrown
    :param times: The number of times to repeat the wrapped function/method
    :type times: Int
    :param Exceptions: Lists of exceptions that trigger a retry attempt
    :type Exceptions: Tuple of Exceptions
    """

    def decorator(func):
        def newfn(*args, **kwargs):
            attempt = 1
            while attempt <= times:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    az_e = AzureMLException._with_error(AzureMLError.create(LLMInternalError, error=e))
                    ex_msg = "Exception thrown when attempting to run {}, attempt {} of {}".format(
                        func.__name__, attempt, times
                    )
                    logger.warning(ex_msg)
                    if attempt == times:
                        logger.warning("Retried {} times when calling {}, now giving up!".format(times, func.__name__))
                        raise
                    attempt += 1
            return func(*args, **kwargs)

        return newfn

    return decorator


def remove_PII():
    """TODO"""
    raise NotImplementedError()
