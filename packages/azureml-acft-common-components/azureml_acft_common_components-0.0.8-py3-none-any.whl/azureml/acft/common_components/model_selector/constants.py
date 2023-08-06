# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Constants for model selector component."""

from dataclasses import dataclass


class ModelSelectorConstants:
    """String constants for model selector component."""

    PYTORCH_MODEL_PATH = "pytorch_model_path"
    MLFLOW_MODEL_PATH = "mlflow_model_path"
    MODEL_NAME = "model_name"
    MLFLOW_MODEL_DATA_PATH = "data"


@dataclass
class ModelSelectorDefaults:
    """Data class for model selector defaults."""

    MODEL_SELECTOR_ARGS_SAVE_PATH = "model_selector_args.json"
    MLFLOW_MODEL_DIRECTORY = "model"
    PYTORCH_MODEL_DIRECTORY = "model"
    # Mandetory name for HF trainer.
    MODEL_CHECKPOINT_FILE_NAME = "pytorch_model.bin"
