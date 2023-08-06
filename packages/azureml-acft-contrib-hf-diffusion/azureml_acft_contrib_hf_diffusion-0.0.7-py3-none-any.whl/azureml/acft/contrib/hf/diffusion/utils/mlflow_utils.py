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
mlflow utilities
"""
from pathlib import Path
import json
import shutil
import yaml
from distutils.dir_util import copy_tree
from typing import List, Union, Optional

from pathlib import Path

from ..constants.constants import MLFlowHFFlavourConstants

from ..diffusion_auto.model import StableDiffusionPipeline, AzuremlStableDiffusionPipeline

from transformers import TrainerCallback, TrainingArguments, TrainerState, TrainerControl
from transformers import PreTrainedModel
from torch_ort import ORTModule

from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.acft.accelerator.utils.error_handling.exceptions import LLMException
from azureml.acft.accelerator.utils.error_handling.error_definitions import LLMInternalError

from azureml.acft.accelerator.utils.logging_utils import get_logger_app
import azureml.evaluate.mlflow as mlflow

from .mlflow_preprocess import prepare_mlflow_preprocess, restructure_mlflow_acft_code


logger = get_logger_app()


class SaveMLflowModelCallback(TrainerCallback):
    """
    A [`TrainerCallback`] that sends the logs to [AzureML](https://pypi.org/project/azureml-sdk/).
    """

    def __init__(
        self,
        mlflow_model_save_path: Union[str, Path],
        mlflow_infer_params_file_path: Union[str, Path],
        mlflow_task_type: str,
        model_name: str,
        model_name_or_path: Optional[str] = None,
        class_names: Optional[List[str]] = None,
        **kwargs
    ) -> None:
        """
        init azureml_run which is azureml Run object
        """
        self.mlflow_model_save_path = mlflow_model_save_path
        self.mlflow_infer_params_file_path = mlflow_infer_params_file_path
        self.mlflow_task_type = mlflow_task_type
        self.class_names = class_names
        self.model_name = model_name
        self.model_name_or_path = model_name_or_path

    def on_train_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs):
        """
        Event called at the end of training.
        Save MLflow model at the end of training

        Model and Tokenizer information is part of kwargs
        """

        model, tokenizer = kwargs["model"], kwargs["tokenizer"]

        # saving the mlflow on world process 0
        if state.is_world_process_zero:
            # tokenization parameters for inference
            # task related parameters
            # with open(self.mlflow_infer_params_file_path, 'r') as fp:
            #     mlflow_inference_params = json.load(fp)

            # misc_conf = {
            #     MLFlowHFFlavourConstants.TASK_TYPE: self.mlflow_task_type,
            #     MLFlowHFFlavourConstants.TRAIN_LABEL_LIST: self.class_names,
            #     MLFlowHFFlavourConstants.HUGGINGFACE_ID: self.model_name_or_path,
            #     **mlflow_inference_params,
            # }
            # files_list = prepare_mlflow_preprocess()
            # model_artifact_path = "llm_multiclass_model"
            # conda_env = {
            #     'channels': ['conda-forge'],
            #     'dependencies': [
            #         'python=3.8.8',
            #         'pip',
            #         {'pip': [
            #         'mlflow',
            #         'torch==1.12.0',
            #         'transformers==4.6.0',
            #     ]}
            #     ],
            #     'name': 'mlflow-env'
            # }
            if isinstance(model, PreTrainedModel):
                acft_model = model
            elif isinstance(model, ORTModule) and hasattr(model, "module"):
                acft_model = model
            elif isinstance(model, AzuremlStableDiffusionPipeline):
                acft_model = model
            else:
                raise LLMException._with_error(
                    AzureMLError.create(LLMInternalError, error=(
                        f"Got unexpected model - {model}"
                    ))
                )
            # mlflow.hftransformers.save_model(
            #     acft_model, self.mlflow_model_save_path, tokenizer, model.config, misc_conf,)
            #     #code_paths=files_list, artifact_path=model_artifact_path, conda_env=conda_env,)
            # restructure_mlflow_acft_code(self.mlflow_model_save_path)
            # logger.info("Saved as mlflow model at {}".format(self.mlflow_model_save_path))

            if isinstance(self.mlflow_model_save_path, str):
                output_dir = Path(self.mlflow_model_save_path)
            else:
                output_dir = self.mlflow_model_save_path
                self.mlflow_model_save_path = str(self.mlflow_model_save_path)

            output_dir.mkdir(exist_ok=True, parents=True)
            mlflow_output_dir = output_dir
            mlflow_data_dir = Path.joinpath(mlflow_output_dir, "data")
            pipeline = StableDiffusionPipeline.from_pretrained(
                acft_model.hf_model_name, # type: ignore
                text_encoder=acft_model.text_encoder, # type: ignore
                vae=acft_model.vae, # type: ignore
                unet=acft_model.unet, # type: ignore
                revision=acft_model.revision, # type: ignore
            )
            pipeline.save_pretrained(str(mlflow_data_dir))  # type: ignore

            assets_folder = Path("./assets")
            # TODO Hardcoing model index.json
            shutil.copy(
                str(Path.joinpath(assets_folder, "model_index.json")),
                str(Path.joinpath(mlflow_data_dir, "model_index.json"))
            )

            # TODO copying mlflow assets to output for deployment
            copy_tree(str(assets_folder), str(mlflow_output_dir))
            Path.joinpath(mlflow_output_dir, "model_index.json").unlink()

            # save LICENSE file to MlFlow model
            if self.model_name_or_path:
                license_file_path = Path(self.model_name_or_path, MLFlowHFFlavourConstants.LICENSE_FILE)
                if license_file_path.is_file():
                    shutil.copy(str(license_file_path), self.mlflow_model_save_path)
                    logger.info("LICENSE file is copied to pytorch model folder")

            # write model_name to MLModel file
            mlflow_file = str(Path.joinpath(mlflow_output_dir, MLFlowHFFlavourConstants.MISC_CONFIG_FILE))
            mlflow_data = None
            with open(mlflow_file, "r") as fp:
                mlflow_data = yaml.safe_load(fp)
            if mlflow_data and mlflow_data["flavors"]:
                if "pyfunc" not in mlflow_data["flavors"]:
                    mlflow_data["flavors"]["pyfunc"] = {}
                mlflow_data["flavors"]["pyfunc"][MLFlowHFFlavourConstants.HUGGINGFACE_ID] = self.model_name
            with open(mlflow_file, "w") as fp:
                yaml.dump(mlflow_data, fp)
            
            logger.info("Saved as mlflow model at {}".format(self.mlflow_model_save_path))

