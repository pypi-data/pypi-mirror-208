# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Copyright 2020 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------------------------------------
"""
model selector utils
"""

import os
from pathlib import Path
from typing import Dict, Any, Union
import shutil
import yaml
import json
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient

from ..constants.constants import SaveFileConstants, MLFlowHFFlavourConstants

from ..base_runner import STABLE_DIFFUSION_SUPPORTED_MODELS

from azureml.acft.accelerator.utils.logging_utils import get_logger_app
from azureml.acft.accelerator.utils.error_handling.exceptions import LLMException, ValidationException
from azureml.acft.accelerator.utils.error_handling.error_definitions import LLMInternalError, ModelNotSupported
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore


logger = get_logger_app()


MODEL_REGISTRY_NAME = "azureml-preview"


def validate_diffusion_model(model_name: str) -> None:
    if model_name not in STABLE_DIFFUSION_SUPPORTED_MODELS:
        raise ValidationException._with_error(
            AzureMLError.create(ModelNotSupported, ModelName=model_name)
        )


def get_model_name_from_pytorch_model(model_path: str) -> str:
    """
    Fetch model_name information from pytorch model metadata file
    """
    finetune_args_file = Path(model_path, SaveFileConstants.FINETUNE_ARGS_SAVE_PATH)

    # load the metadata file
    try:
        with open(finetune_args_file, "r") as rptr:
            finetune_args = json.load(rptr)
    except Exception as e:
        raise LLMException._with_error(
            AzureMLError.create(LLMInternalError, error=(
                f"Failed to load {finetune_args_file}\n"
                f"{e}"
                )
            )
        )

    # check for `model_name` in metadata file
    if finetune_args and "model_name" in finetune_args:
        return finetune_args["model_name"]
    else:
       raise LLMException._with_error(
            AzureMLError.create(LLMInternalError, error=(
                f"model_name is missing in "
                f"{SaveFileConstants.FINETUNE_ARGS_SAVE_PATH} file"
                )
            )
        )


def get_model_name_from_mlflow_model(model_path: str) -> str:
    """
    Fetch model_name information from mlflow metadata file
    """
    mlflow_config_file = Path(model_path, MLFlowHFFlavourConstants.MISC_CONFIG_FILE)

    # load mlflow config file
    try:
        with open(mlflow_config_file, "r") as rptr:
            mlflow_data = yaml.safe_load(rptr)
    except Exception as e:
        raise LLMException._with_error(
            AzureMLError.create(LLMInternalError, error=(
                f"Failed to load {mlflow_config_file}\n"
                f"{e}"
                )
            )
        )

    # fetch the model name
    try:
        if mlflow_data and MLFlowHFFlavourConstants.HUGGINGFACE_ID in mlflow_data["flavors"]["hftransformers"]:
            return mlflow_data["flavors"]["hftransformers"][MLFlowHFFlavourConstants.HUGGINGFACE_ID]
    except Exception as e:
        raise LLMException._with_error(
            AzureMLError.create(LLMInternalError, error=(
                "{Invalid mlflow config file}\n"
                f"{e}"
                )
            )
        )

def convert_mlflow_model_to_pytorch_model(mlflow_model_path: Union[str, Path], download_dir: Path):
    """
    converts mlflow model to pytorch model
    """
    download_dir.mkdir(exist_ok=True, parents=True)
    try:
        # copy the model files
        shutil.copytree(
            Path(mlflow_model_path, 'data/model'),
            download_dir,
            dirs_exist_ok=True
        )
        # copy config files
        shutil.copytree(
            Path(mlflow_model_path, 'data/config'),
            download_dir,
            dirs_exist_ok=True
        )
        # copy tokenizer files
        shutil.copytree(
            Path(mlflow_model_path, 'data/tokenizer'),
            download_dir,
            dirs_exist_ok=True
        )
        # copy LICENSE file
        license_file_path = Path(mlflow_model_path, MLFlowHFFlavourConstants.LICENSE_FILE)
        if license_file_path.is_file():
            shutil.copy(str(license_file_path), download_dir)
    except Exception as e:
        shutil.rmtree(download_dir, ignore_errors=True)
        raise LLMException._with_error(
            AzureMLError.create(
                LLMInternalError,
                error=(
                    "Failed to convert mlflow model to pytorch model.\n"
                    f"{e}"
                )
            )
        )


def download_model_from_registry(model_name: str, download_dir: str):
    """
    downloads mlflow models from azureml-preview registry
    """
    # in azure-ai-ml-1.0.0 DefaultAzureCredential handles ManagedIdentityCredential internally
    client_id = os.environ.get("DEFAULT_IDENTITY_CLIENT_ID", None)
    if client_id:
        logger.info("Using DEFAULT_IDENTITY_CLIENT_ID")
        credential = DefaultAzureCredential(managed_identity_client_id=client_id)
    else:
        credential = DefaultAzureCredential()
    registry_mlclient = MLClient(credential=credential, registry_name=MODEL_REGISTRY_NAME)
    registry_models_list = registry_mlclient.models.list(name=model_name)
    registry_models_versions = [int(model.version) for model in registry_models_list]

    # download the model from registry - mlflow model
    model_tmp_download_path = Path(download_dir, "azuremlft_download")
    if len(registry_models_versions) > 0:
        model_version = str(max(registry_models_versions))
        registry_mlclient.models.download(
            name=model_name,
            version=model_version,
            download_path=model_tmp_download_path,
        )
        logger.info(f"Model {model_name}/{model_version} is downloaded")
        mlflow_model_dir = Path(
            model_tmp_download_path, model_name,
            MLFlowHFFlavourConstants.MODEL_ROOT_DIRECTORY
        )
        model_save_path = Path(download_dir, model_name)
        # convert mlflow model to pytorch model and save it to model_save_path
        convert_mlflow_model_to_pytorch_model(mlflow_model_dir, model_save_path)
    else:
        raise LLMException._with_error(
            AzureMLError.create(
                LLMInternalError,
                error="Model not found in registry"
            )
        )


def model_selector(model_selector_args: Dict[str, Any]):
    """
    Downloads model from azureml-preview registry if present
    Prepares model for continual finetuning
    Save model selector args
    """
    logger.info(f"Model Selector args - {model_selector_args}")
    # pytorch model port
    pytorch_model_path = model_selector_args.get("pytorch_model_path", None)
    # mlflow model port
    mlflow_model_path = model_selector_args.get("mlflow_model_path", None)

    # if both pytorch and mlflow model ports are specified, pytorch port takes precedence
    if pytorch_model_path is not None:
        logger.info("Working with pytorch model")
        # copy model to download_dir
        model_name = get_model_name_from_pytorch_model(pytorch_model_path)
        validate_diffusion_model(model_name)
        model_selector_args["model_name"] = model_name
        download_dir = Path(model_selector_args["output_dir"], model_name)
        download_dir.mkdir(exist_ok=True, parents=True)
        try:
            shutil.copytree(pytorch_model_path, download_dir, dirs_exist_ok=True)
        except Exception as e:
            shutil.rmtree(download_dir, ignore_errors=True)
            raise LLMException._with_error(
                AzureMLError.create(
                    LLMInternalError,
                    error=(
                        "shutil copy failed.\n"
                        f"{e}"
                    )
                )
            )
    elif mlflow_model_path is not None:
        logger.info("Working with Mlflow model")
        model_name = get_model_name_from_mlflow_model(mlflow_model_path)
        validate_diffusion_model(model_name)
        model_selector_args["model_name"] = model_name
        # convert mlflow model to pytorch model and save it to model_save_path
        download_dir = Path(model_selector_args["output_dir"], model_name)
        convert_mlflow_model_to_pytorch_model(mlflow_model_path, download_dir)
    else:
        try:
            logger.info(f'Downloading the model from registry to {model_selector_args["output_dir"]}')
            download_model_from_registry(model_selector_args["model_name"], model_selector_args["output_dir"])
        except Exception as e:
            # TODO Check why shutil rmtree is called
            # shutil.rmtree(model_selector_args["output_dir"], ignore_errors=True)
            logger.info(
                f'Unable to download model, will fetch {model_selector_args["model_name"]} model while fine-tuning',
                exc_info=True
            )

    # Saving model selector args
    model_selector_args_save_path = os.path.join(model_selector_args["output_dir"], SaveFileConstants.MODEL_SELECTOR_ARGS_SAVE_PATH)
    logger.info(f"Saving the model selector args to {model_selector_args_save_path}")
    with open(model_selector_args_save_path, "w") as wptr:
        json.dump(model_selector_args, wptr, indent=2)
