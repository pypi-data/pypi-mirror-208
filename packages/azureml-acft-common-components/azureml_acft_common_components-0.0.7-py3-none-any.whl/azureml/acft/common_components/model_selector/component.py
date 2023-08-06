# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""For model selector component."""

import json
import os
import shutil
from pathlib import Path
from typing import Union

from azureml._common._error_definition.azureml_error import AzureMLError

from azureml.acft.common_components.utils.error_handling.error_definitions import InvalidMlflowModelFormat, \
    ModelInputEmpty
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTValidationException
from azureml.acft.common_components.utils.logging_utils import get_logger_app
from .constants import (
    ModelSelectorConstants,
    ModelSelectorDefaults
)

logger = get_logger_app(__name__)


class ModelSelector:
    """Model selector class to select the model and store the arguments to json file."""
    def __init__(
        self,
        pytorch_model: str = None,
        mlflow_model: str = None,
        model_name: str = None,
        output_dir: str = None,
        **kwargs,
    ) -> None:
        """Default implementation for model selector. Override the functions for custom implementation.

        :param pytorch_model: asset path of pytorch model, defaults to None
        :type pytorch_model: str, optional
        :param mlflow_model: asset path of mlflow model, defaults to None
        :type mlflow_model: str, optional
        :param model_name: model name from the framework (i.e., HF), defaults to None
        :type model_name: str, optional
        :param output_dir: path to store arguments and model, defaults to None
        :type output_dir: str, optional
        """
        self.pytorch_model = pytorch_model
        self.mlflow_model = mlflow_model
        self.output_dir = output_dir
        self.model_name = model_name
        self.keyword_arguments = kwargs

    def _download_pytorch_model_from_registry(self) -> None:
        """Download pytorch model from AzureML registry"""
        model_path = os.path.join(
            self.output_dir, ModelSelectorDefaults.PYTORCH_MODEL_DIRECTORY
        )
        ModelSelector._copy_directories(self.pytorch_model, model_path)
        logger.info(
            f"Downloaded pytorch model from {self.pytorch_model} to {model_path}."
        )

    def _download_mlflow_model_from_registry(self) -> None:
        """Download mlflow model from AzureML registry"""
        model_path = os.path.join(
            self.output_dir, ModelSelectorDefaults.MLFLOW_MODEL_DIRECTORY
        )
        ModelSelector.convert_mlflow_model_to_pytorch_model(self.mlflow_model, Path(model_path))
        logger.info(
            f"Downloaded mlflow model from {self.mlflow_model} to {model_path}."
        )

    def _prepare_and_logs_arguments(self) -> None:
        """Update the keyword arguments (if present) with required key-val items and
        Store the model selector arguments to json file.
        """
        arguments = {
            ModelSelectorConstants.MLFLOW_MODEL_PATH: self.mlflow_model,
            ModelSelectorConstants.PYTORCH_MODEL_PATH: self.pytorch_model,
            ModelSelectorConstants.MODEL_NAME: self.model_name,
        }

        if self.keyword_arguments:
            self.keyword_arguments.update(arguments)
        else:
            self.keyword_arguments = arguments

        os.makedirs(self.output_dir, exist_ok=True)
        model_selector_args_save_path = os.path.join(
            self.output_dir, ModelSelectorDefaults.MODEL_SELECTOR_ARGS_SAVE_PATH
        )
        logger.info(
            f"Saving the model selector args to {model_selector_args_save_path}"
        )
        with open(model_selector_args_save_path, "w") as output_file:
            json.dump(self.keyword_arguments, output_file, indent=2)

    @staticmethod
    def _copy_directories(asset_path: str, destination: str) -> None:
        """Recursively copy asset to destination

        :param asset_path: asset path of Azure ML
        :type asset_path: str
        :param destination: destination path
        :type destination: str
        """
        os.makedirs(destination, exist_ok=True)
        shutil.copytree(asset_path, destination, dirs_exist_ok=True)

    def convert_mlflow_model_to_pytorch_model(
            mlflow_model_path: Union[str, Path],
            download_dir: Path) -> None:
        """
        Download the mlflow model assets(model, config and proprocessor.json file)
        in the download directory to have similar directory structure as the pytorch model.

        :param mlflow_model_path: Path of the mlflow model
        :type mlflow_model_path: Union[str, Path]
        :param download_dir: Destination directory to download the model
        :type download_dir: Path
        """

        os.makedirs(download_dir, exist_ok=True)
        try:
            DATA_DIR = ModelSelectorConstants.MLFLOW_MODEL_DATA_PATH
            model_dir = Path(mlflow_model_path, f'{DATA_DIR}/model')
            config_dir = Path(mlflow_model_path, f'{DATA_DIR}/config')
            tokenizer_dir = Path(mlflow_model_path, f'{DATA_DIR}/tokenizer')

            # copy the model
            shutil.copytree(model_dir, download_dir, dirs_exist_ok=True)

            # copy the config files
            shutil.copytree(config_dir, download_dir, dirs_exist_ok=True)

            # copy tokenizer files
            shutil.copytree(tokenizer_dir, download_dir, dirs_exist_ok=True)
        except Exception:
            shutil.rmtree(download_dir, ignore_errors=True)
            directories = f" '{model_dir}', '{config_dir}', '{tokenizer_dir}' "
            raise ACFTValidationException._with_error(
                AzureMLError.create(
                    InvalidMlflowModelFormat, directories
                )
            )

    def run_workflow(self):
        """If model asset path is provided then it will download the model. Pytorch model will take preference
        over mlflow model. If model name is provided then, it will not download model from framework hub.
        It's responsibility of downstream component (e.g., finetune) to load the model.

        :raises ArgumentException._with_error: Raise exception if model ports or model name is not provided.
        """
        if self.pytorch_model is not None:
            self._download_pytorch_model_from_registry()
            self.pytorch_model = ModelSelectorDefaults.PYTORCH_MODEL_DIRECTORY
            self.mlflow_model = None
        elif self.mlflow_model is not None:
            self._download_mlflow_model_from_registry()
            self.mlflow_model = ModelSelectorDefaults.MLFLOW_MODEL_DIRECTORY
        elif self.model_name is None:
            raise ACFTValidationException._with_error(
                AzureMLError.create(
                    ModelInputEmpty, argument_name="Model ports and model_name"
                )
            )
        self._prepare_and_logs_arguments()
