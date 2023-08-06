# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
The ``mlflow.pytorch`` module provides an API for logging and loading PyTorch models. This module
exports PyTorch models with the following flavors:

PyTorch (native) format
    This is the main flavor that can be loaded back into PyTorch.
:py:mod:`mlflow.pyfunc`
    Produced for use by generic pyfunc-based deployment tools and batch inference.
"""
import importlib
import logging
import os
import yaml
import warnings

import numpy as np
import pandas as pd
import posixpath

from transformers import PretrainedConfig, PreTrainedTokenizerBase, PreTrainedModel, AutoConfig, pipeline
import azureml.evaluate.mlflow as mlflow
import shutil
from azureml.evaluate.mlflow import pyfunc, aml
from mlflow.exceptions import MlflowException
from mlflow.models import Model, ModelSignature
from mlflow.models.model import MLMODEL_FILE_NAME
from mlflow.models.utils import ModelInputExample, _save_example
from mlflow.protos.databricks_pb2 import RESOURCE_DOES_NOT_EXIST
from mlflow.tracking.artifact_utils import _download_artifact_from_uri
from mlflow.utils.environment import (
    _mlflow_conda_env,
    _validate_env_arguments,
    _process_pip_requirements,
    _process_conda_env,
    _CONDA_ENV_FILE_NAME,
    _REQUIREMENTS_FILE_NAME,
    _CONSTRAINTS_FILE_NAME,
    _PYTHON_ENV_FILE_NAME,
    _PythonEnv,
)
from mlflow.utils.requirements_utils import _get_pinned_requirement
from mlflow.utils.docstring_utils import format_docstring, LOG_MODEL_PARAM_DOCS
from mlflow.utils.file_utils import (
    TempDir,
    write_to,
)
from mlflow.utils.model_utils import (
    _get_flavor_configuration,
    _validate_and_copy_code_paths,
    _add_code_from_conf_to_system_path,
    _validate_and_prepare_target_save_path,
)
from mlflow.tracking._model_registry import DEFAULT_AWAIT_MAX_SLEEP_SECONDS

from azureml.evaluate.mlflow.hftransformers.constants import Constants

FLAVOR_NAME = "hftransformers"

_HFMODEL_PATH = "model"
_HF_TOKENIZER_PATH = "tokenizer"
_HF_CONFIG_PATH = "config"
_EXTRA_FILES_KEY = "extra_files"
_REQUIREMENTS_FILE_KEY = "requirements_file"

_logger = logging.getLogger(__name__)


def get_default_pip_requirements():
    """
    :return: A list of default pip requirements for MLflow Models produced by this flavor.
             Calls to :func:`save_model()` and :func:`log_model()` produce a pip environment
             that, at minimum, contains these requirements.
    """
    return list(
        map(
            _get_pinned_requirement,
            [
                "torch",
                "transformers",
                # We include CloudPickle in the default environment because
                # it's required by the default pickle module used by `save_model()`
                # and `log_model()`: `mlflow.pytorch.pickle_module`.
                "cloudpickle",
            ],
        )
    )


def get_default_conda_env():
    """
    :return: The default Conda environment as a dictionary for MLflow Models produced by calls to
             :func:`save_model()` and :func:`log_model()`.

    .. code-block:: python
        :caption: Example

        import mlflow.hftransformer

        # LogHFTransformer model
        with mlflow.start_run() as run:
            mlflow.hftransformer.log_model(model, "model", tokenizer)

        # Fetch the associated conda environment
        env = mlflow.hftransformer.get_default_conda_env()
        print("conda env: {}".format(env))

    .. code-block:: text
        :caption: Output

        conda env {'name': 'mlflow-env',
                   'channels': ['conda-forge'],
                   'dependencies': ['python=3.7.5',
                                    {'pip': ['torch==1.5.1',
                                             'mlflow',
                                             'cloudpickle==1.6.0']}]}
    """
    return _mlflow_conda_env(additional_pip_deps=get_default_pip_requirements())


@format_docstring(LOG_MODEL_PARAM_DOCS.format(package_name=FLAVOR_NAME))
def log_model(
        hf_model,
        artifact_path,
        tokenizer=None,
        config=None,
        hf_conf=None,
        conda_env=None,
        code_paths=None,
        registered_model_name=None,
        signature: ModelSignature = None,
        input_example: ModelInputExample = None,
        await_registration_for=DEFAULT_AWAIT_MAX_SLEEP_SECONDS,
        requirements_file=None,
        extra_files=None,
        pip_requirements=None,
        extra_pip_requirements=None,
        **kwargs,
):
    """
    Log a PyTorch model as an MLflow artifact for the current run.

        .. warning::

            Log the model with a signature to avoid inference errors.
            If the model is logged without a signature, the MLflow Model Server relies on the
            default inferred data type from NumPy. However, PyTorch often expects different
            defaults, particularly when parsing floats. You must include the signature to ensure
            that the model is logged with the correct data type so that the MLflow model server
            can correctly provide valid input.

    :param hf_conf: Dictionary containing supplementary config
    :param hf_model: Huggingface model to be saved.

    :param artifact_path: Run-relative artifact path.
    :param tokenizer: Tokenizer used for training
    :param config: config used for training
    :param conda_env: {{ conda_env }}
    :param code_paths: A list of local filesystem paths to Python file dependencies (or directories
                       containing file dependencies). These files are *prepended* to the system
                       path when the model is loaded.

    :param registered_model_name: If given, create a model version under
                                  ``registered_model_name``, also creating a registered model if one
                                  with the given name does not exist.

    :param signature: :py:class:`ModelSignature <mlflow.models.ModelSignature>`
                      describes model input and output :py:class:`Schema <mlflow.types.Schema>`.
                      The model signature can be :py:func:`inferred <mlflow.models.infer_signature>`
                      from datasets with valid model input (e.g. the training dataset with target
                      column omitted) and valid model output (e.g. model predictions generated on
                      the training dataset), for example:

                      .. code-block:: python

                        from mlflow.models.signature import infer_signature
                        train = df.drop_column("target_label")
                        predictions = ... # compute model predictions
                        signature = infer_signature(train, predictions)
    :param input_example: Input example provides one or several instances of valid
                          model input. The example can be used as a hint of what data to feed the
                          model. The given example can be a Pandas DataFrame where the given
                          example will be serialized to json using the Pandas split-oriented
                          format, or a numpy array where the example will be serialized to json
                          by converting it to a list. Bytes are base64-encoded.

    :param await_registration_for: Number of seconds to wait for the model version to finish
                            being created and is in ``READY`` status. By default, the function
                            waits for five minutes. Specify 0 or None to skip waiting.

    :param requirements_file:

        .. warning::

            ``requirements_file`` has been deprecated. Please use ``pip_requirements`` instead.

        A string containing the path to requirements file. Remote URIs are resolved to absolute
        filesystem paths. For example, consider the following ``requirements_file`` string:

        .. code-block:: python

            requirements_file = "s3://my-bucket/path/to/my_file"

        In this case, the ``"my_file"`` requirements file is downloaded from S3. If ``None``,
        no requirements file is added to the model.

    :param extra_files: A list containing the paths to corresponding extra files. Remote URIs
                      are resolved to absolute filesystem paths.
                      For example, consider the following ``extra_files`` list -

                      extra_files = ["s3://my-bucket/path/to/my_file1",
                                    "s3://my-bucket/path/to/my_file2"]

                      In this case, the ``"my_file1 & my_file2"`` extra file is downloaded from S3.

                      If ``None``, no extra files are added to the model.
    :param pip_requirements: {{ pip_requirements }}
    :param extra_pip_requirements: {{ extra_pip_requirements }}
    :param kwargs: kwargs to pass to ``torch.save`` method.
    :return: A :py:class:`ModelInfo <mlflow.models.model.ModelInfo>` instance that contains the
             metadata of the logged model.

    """
    return Model.log(
        hf_model=hf_model,
        artifact_path=artifact_path,
        tokenizer=tokenizer,
        config=config,
        hf_conf=hf_conf,
        flavor=mlflow.hftransformers,
        conda_env=conda_env,
        code_paths=code_paths,
        registered_model_name=registered_model_name,
        signature=signature,
        input_example=input_example,
        await_registration_for=await_registration_for,
        requirements_file=requirements_file,
        extra_files=extra_files,
        pip_requirements=pip_requirements,
        extra_pip_requirements=extra_pip_requirements,
        **kwargs,
    )


def _save_hf_model(
        model_data_path,
        hf_model,
        tokenizer,
        config):
    """
    Save The incoming HF model
    :param model_data_path: Model Data path
    :type model_data_path: str
    :param hf_model: Model
    :type hf_model: PretrainedModel | str
    :param tokenizer: Tokenizer
    :type tokenizer: PreTrainedTokenizerBase | str | None
    :param config: AutoConfig
    :type config: PretrainedConfig | str | None
    """
    model_path = os.path.join(model_data_path, _HFMODEL_PATH)
    tokenizer_path = os.path.join(model_data_path, _HF_TOKENIZER_PATH)
    config_path = os.path.join(model_data_path, _HF_CONFIG_PATH)

    def save_or_copy(obj_type, obj, base_class, path_to_save):
        if isinstance(obj, base_class) or hasattr(obj, 'save_pretrained'):
            obj.save_pretrained(path_to_save)
        elif isinstance(obj, str):
            shutil.copytree(obj, path_to_save)
        else:
            _logger.error(
                f"The {obj_type} should be either a instance of {base_class}, or should be a path to the {obj_type}")

    save_or_copy("model", hf_model, PreTrainedModel, model_path)
    if tokenizer is not None:
        save_or_copy("tokenizer", tokenizer, PreTrainedTokenizerBase, tokenizer_path)
    if config is not None:
        save_or_copy("config", config, PretrainedConfig, config_path)


def _get_tokenizer_class(tokenizer, hf_tokenizer_class):
    if hf_tokenizer_class is not None:
        return hf_tokenizer_class
    if hasattr(tokenizer, 'save_pretrained'):
        return tokenizer.__class__.__name__
    return 'AutoTokenizer'


def _get_config_class(config, hf_config_class):
    if hf_config_class is not None:
        return hf_config_class
    if hasattr(config, 'save_pretrained'):
        return config.__class__.__name__
    return 'AutoConfig'


def _get_pretrained_class(model, config, hf_pretrained_class=None):
    """
    Function to get the Pretrained class of the model
    ToDo:
    :param model: HF model
    :type model: PreTrainedModel|str
    :param config: AutoConfig
    :type config: PretrainedConfig | str
    :return: Model Architecture class
    :rtype: str
    """
    if isinstance(model, PreTrainedModel):
        return model.__class__.__name__
    if hf_pretrained_class is not None:
        return hf_pretrained_class

    _logger.warning("'hf_pretrained_class' is an expected parameter in case of model not being an instance of "
                    "'PreTrainedModel'")
    if isinstance(config, str):
        config = AutoConfig.from_pretrained(config)
    if hasattr(config, "architectures") and len(config.architectures) > 0:
        _logger.warning("Resolving AutoModel base class from config.architectures. Please note that this might lead "
                        "to inconsistencies in preictions")
        return config.architectures[0]
    _logger.warning(
        "AutoConfig does not has 'architectures' defined. Using AutoModel base class to load the model which might "
        "lead to incorrect results")
    return "AutoModel"


def _add_package_if_not_exists_conda(conda_env, package):
    pip_dependencies = conda_env.get("dependencies", [])
    for i, dep in enumerate(pip_dependencies):
        if isinstance(dep, dict) and "pip" in dep and isinstance(dep["pip"], list):
            for item in dep["pip"]:
                if package in item:
                    return conda_env
            conda_env["dependencies"][i]["pip"].append(package)
            return conda_env
    return conda_env


def _add_package_if_not_exists_pip(pip_list, package):
    """
    Check if <package> str exists in pip_list
    """
    for item in pip_list:
        if package in item:
            return pip_list
    pip_list.append(package)
    return pip_list


@format_docstring(LOG_MODEL_PARAM_DOCS.format(package_name=FLAVOR_NAME))
def save_model(
        hf_model,
        path,
        tokenizer=None,
        config=None,
        hf_conf=None,
        conda_env=None,
        mlflow_model=None,
        code_paths=None,
        pickle_module=None,
        signature: ModelSignature = None,
        input_example: ModelInputExample = None,
        requirements_file=None,
        extra_files=None,
        pip_requirements=None,
        extra_pip_requirements=None,
        **kwargs,
):
    """
    Save a HF model to a path on the local file system.

    :param hf_conf: Dictionary containing additional arguments for prediction, task and miscellaneous args
    :param hf_model: PyTorch model to be saved. Can be either an eager model (subclass of
                          ``torch.nn.Module``) or scripted model prepared via ``torch.jit.script``
                          or ``torch.jit.trace``.

                          The model accept a single ``torch.FloatTensor`` as
                          input and produce a single output tensor.

                          If saving an eager model, any code dependencies of the
                          model's class, including the class definition itself, should be
                          included in one of the following locations:

                          - The package(s) listed in the model's Conda environment, specified
                            by the ``conda_env`` parameter.
                          - One or more of the files specified by the ``code_paths`` parameter.

    :param path: Local path where the model is to be saved.
    :param tokenizer
    :param config
    :param conda_env: {{ conda_env }}
    :param mlflow_model: :py:mod:`mlflow.models.Model` this flavor is being added to.
    :param code_paths: A list of local filesystem paths to Python file dependencies (or directories
                       containing file dependencies). These files are *prepended* to the system
                       path when the model is loaded.
    :param pickle_module: The module that PyTorch should use to serialize ("pickle") the specified
                          ``pytorch_model``. This is passed as the ``pickle_module`` parameter
                          to ``torch.save()``. By default, this module is also used to
                          deserialize ("unpickle") the PyTorch model at load time.

    :param signature: :py:class:`ModelSignature <mlflow.models.ModelSignature>`
                      describes model input and output :py:class:`Schema <mlflow.types.Schema>`.
                      The model signature can be :py:func:`inferred <mlflow.models.infer_signature>`
                      from datasets with valid model input (e.g. the training dataset with target
                      column omitted) and valid model output (e.g. model predictions generated on
                      the training dataset), for example:

                      .. code-block:: python

                        from mlflow.models.signature import infer_signature
                        train = df.drop_column("target_label")
                        predictions = ... # compute model predictions
                        signature = infer_signature(train, predictions)
    :param input_example: Input example provides one or several instances of valid
                          model input. The example can be used as a hint of what data to feed the
                          model. The given example can be a Pandas DataFrame where the given
                          example will be serialized to json using the Pandas split-oriented
                          format, or a numpy array where the example will be serialized to json
                          by converting it to a list. Bytes are base64-encoded.

    :param requirements_file:

        .. warning::

            ``requirements_file`` has been deprecated. Please use ``pip_requirements`` instead.

        A string containing the path to requirements file. Remote URIs are resolved to absolute
        filesystem paths. For example, consider the following ``requirements_file`` string:

        .. code-block:: python

            requirements_file = "s3://my-bucket/path/to/my_file"

        In this case, the ``"my_file"`` requirements file is downloaded from S3. If ``None``,
        no requirements file is added to the model.

    :param extra_files: A list containing the paths to corresponding extra files. Remote URIs
                      are resolved to absolute filesystem paths.
                      For example, consider the following ``extra_files`` list -

                      extra_files = ["s3://my-bucket/path/to/my_file1",
                                    "s3://my-bucket/path/to/my_file2"]

                      In this case, the ``"my_file1 & my_file2"`` extra file is downloaded from S3.

                      If ``None``, no extra files are added to the model.
    :param pip_requirements: {{ pip_requirements }}
    :param extra_pip_requirements: {{ extra_pip_requirements }}
    :param kwargs: kwargs to pass to ``torch.save`` method.

    .. code-block:: python
        :caption: Example

        import os

        import torch
        import mlflow.pytorch

        # Class defined here
        class LinearNNModel(torch.nn.Module):
            ...

        # Initialize our model, criterion and optimizer
        ...

        # Training loop
        ...

        # Save PyTorch models to current working directory
        with mlflow.start_run() as run:
            mlflow.pytorch.save_model(model, "model")

            # Convert to a scripted model and save it
            scripted_pytorch_model = torch.jit.script(model)
            mlflow.pytorch.save_model(scripted_pytorch_model, "scripted_model")

        # Load each saved model for inference
        for model_path in ["model", "scripted_model"]:
            model_uri = "{}/{}".format(os.getcwd(), model_path)
            loaded_model = mlflow.pytorch.load_model(model_uri)
            print("Loaded {}:".format(model_path))
            for x in [6.0, 8.0, 12.0, 30.0]:
                X = torch.Tensor([[x]])
                y_pred = loaded_model(X)
                print("predict X: {}, y_pred: {:.2f}".format(x, y_pred.data.item()))
            print("--")

    .. code-block:: text
        :caption: Output

        Loaded model:
        predict X: 6.0, y_pred: 11.90
        predict X: 8.0, y_pred: 15.92
        predict X: 12.0, y_pred: 23.96
        predict X: 30.0, y_pred: 60.13
        --
        Loaded scripted_model:
        predict X: 6.0, y_pred: 11.90
        predict X: 8.0, y_pred: 15.92
        predict X: 12.0, y_pred: 23.96
        predict X: 30.0, y_pred: 60.13
    """
    if hf_conf is None:
        hf_conf = {}
    import torch
    import transformers

    _validate_env_arguments(conda_env, pip_requirements, extra_pip_requirements)

    path = os.path.abspath(path)
    _validate_and_prepare_target_save_path(path)

    if mlflow_model is None:
        mlflow_model = Model()

    if signature is not None:
        mlflow_model.signature = signature
    if input_example is not None:
        _save_example(mlflow_model, input_example, path)

    code_dir_subpath = _validate_and_copy_code_paths(code_paths, path)

    model_data_subpath = "data"
    model_data_path = os.path.join(path, model_data_subpath)
    os.makedirs(model_data_path)
    _save_hf_model(model_data_path, hf_model, tokenizer, config)
    hf_pretrained_class = _get_pretrained_class(hf_model, config, hf_conf.pop("hf_pretrained_class", None))
    hf_tokenizer_class = _get_tokenizer_class(tokenizer, hf_conf.pop("hf_tokenizer_class", None))
    hf_config_class = _get_config_class(config, hf_conf.pop("hf_config_class", None))

    torchserve_artifacts_config = {}

    if extra_files:
        torchserve_artifacts_config[_EXTRA_FILES_KEY] = []
        if not isinstance(extra_files, list):
            raise TypeError("Extra files argument should be a list")

        with TempDir() as tmp_extra_files_dir:
            for extra_file in extra_files:
                _download_artifact_from_uri(
                    artifact_uri=extra_file, output_path=tmp_extra_files_dir.path()
                )
                rel_path = posixpath.join(_EXTRA_FILES_KEY, os.path.basename(extra_file))
                torchserve_artifacts_config[_EXTRA_FILES_KEY].append({"path": rel_path})
            shutil.move(
                tmp_extra_files_dir.path(),
                posixpath.join(path, _EXTRA_FILES_KEY),
            )

    if requirements_file:

        warnings.warn(
            "`requirements_file` has been deprecated. Please use `pip_requirements` instead.",
            FutureWarning,
            stacklevel=2,
        )

        if not isinstance(requirements_file, str):
            raise TypeError("Path to requirements file should be a string")

        with TempDir() as tmp_requirements_dir:
            _download_artifact_from_uri(
                artifact_uri=requirements_file, output_path=tmp_requirements_dir.path()
            )
            rel_path = os.path.basename(requirements_file)
            torchserve_artifacts_config[_REQUIREMENTS_FILE_KEY] = {"path": rel_path}
            shutil.move(tmp_requirements_dir.path(rel_path), path)
    for key in hf_conf:
        # if getattr(hf_conf[key], 'save_pretrained', None) is not None:
        #     path_to_save = os.path.join(path, key)
        #     hf_conf[key].save_pretrained(path_to_save)
        #     torchserve_artifacts_config[key] = {"path_pretrained_object": key}
        if type(hf_conf[key]) in [list, np.array, np.ndarray] or getattr(hf_conf[key], "__dict__", None) is not None:
            path_to_list = os.path.join(path, key)
            # if not os.path.exists(mlflow_model.artifact_path):
            #     os.mkdir(mlflow_model.artifact_path)
            np.save(path_to_list, hf_conf[key], allow_pickle=True)
            torchserve_artifacts_config[key] = {"path_list": key + ".npy"}
        else:
            torchserve_artifacts_config[key] = hf_conf[key]

    mlflow_model.add_flavor(
        FLAVOR_NAME,
        model_data=model_data_subpath,
        pytorch_version=str(torch.__version__),
        transformers_version=str(transformers.__version__),
        hf_pretrained_class=hf_pretrained_class,
        hf_tokenizer_class=hf_tokenizer_class,
        hf_config_class=hf_config_class,
        code=code_dir_subpath,
        **torchserve_artifacts_config,
    )
    pyfunc.add_to_model(
        mlflow_model,
        loader_module="azureml.evaluate.mlflow.hftransformers",
        data=model_data_subpath,
        code=code_dir_subpath,
        env=_CONDA_ENV_FILE_NAME,
    )
    mlflow_model.save(os.path.join(path, MLMODEL_FILE_NAME))

    if conda_env is None:
        if pip_requirements is None:
            default_reqs = get_default_pip_requirements()
            # To ensure `_load_pyfunc` can successfully load the model during the dependency
            # inference, `mlflow_model.save` must be called beforehand to save an MLmodel file.
            inferred_reqs = mlflow.models.infer_pip_requirements(
                model_data_path,
                FLAVOR_NAME,
                fallback=default_reqs,
            )
            default_reqs = sorted(set(inferred_reqs).union(default_reqs))
        else:
            default_reqs = None
        conda_env, pip_requirements, pip_constraints = _process_pip_requirements(
            default_reqs,
            pip_requirements,
            extra_pip_requirements,
        )
    else:
        conda_env, pip_requirements, pip_constraints = _process_conda_env(conda_env)

    conda_env = _add_package_if_not_exists_conda(conda_env, package=constants.AdditionalPackages.EVALUATE_PACKAGE)
    pip_requirements = _add_package_if_not_exists_pip(pip_requirements,
                                                      package=constants.AdditionalPackages.EVALUATE_PACKAGE)
    with open(os.path.join(path, _CONDA_ENV_FILE_NAME), "w") as f:
        yaml.safe_dump(conda_env, stream=f, default_flow_style=False)

    # Save `constraints.txt` if necessary
    if pip_constraints:
        write_to(os.path.join(path, _CONSTRAINTS_FILE_NAME), "\n".join(pip_constraints))

    if not requirements_file:
        # Save `requirements.txt`
        write_to(os.path.join(path, _REQUIREMENTS_FILE_NAME), "\n".join(pip_requirements))

    _PythonEnv.current().to_yaml(os.path.join(path, _PYTHON_ENV_FILE_NAME))


def _load_object_from_module(module_name, class_name, path_to_obj, **kwargs):
    """

    """
    try:
        model_module = importlib.import_module(module_name)
        object_class = getattr(model_module, class_name)
    except (AttributeError, ImportError) as exc:
        raise MlflowException(
            message=(
                "Failed to import {} class from {}".format(class_name, module_name)
            ),
            error_code=RESOURCE_DOES_NOT_EXIST,
        ) from exc
    loaded_obj = object_class.from_pretrained(path_to_obj, **kwargs)
    return loaded_obj


def _load_model(path, hf_conf):
    """
    :param path: The path to a serialized PyTorch model.
    :param kwargs: Additional kwargs to pass to the PyTorch ``torch.load`` function.
    """
    model_path = os.path.join(path, _HFMODEL_PATH)
    tokenizer_path = os.path.join(path, _HF_TOKENIZER_PATH)
    config_path = os.path.join(path, _HF_CONFIG_PATH)
    task_type = hf_conf.get("task_type", None)
    config_path = config_path if os.path.exists(config_path) else model_path
    tokenizer_path = tokenizer_path if os.path.exists(tokenizer_path) else model_path

    config, tokenizer = None, None
    if hf_conf.get("force_load_config", True):
        config = _load_object_from_module(module_name=hf_conf.get("custom_config_module", "transformers"),
                                          class_name=hf_conf.get("hf_config_class", "AutoConfig"),
                                          path_to_obj=config_path)
    if hf_conf.get("force_load_tokenizer", True):
        tokenizer = _load_object_from_module(module_name=hf_conf.get("custom_tokenizer_module", "transformers"),
                                             class_name=hf_conf.get("hf_tokenizer_class", "AutoTokenizer"),
                                             path_to_obj=tokenizer_path,
                                             config=config)
    hf_model = _load_object_from_module(module_name=hf_conf.get("custom_model_module", "transformers"),
                                        class_name=hf_conf.get("hf_pretrained_class", "AutoModel"),
                                        path_to_obj=model_path,
                                        config=config)
    return task_type, hf_model, tokenizer, config


def load_model(model_uri, dst_path=None, **kwargs):
    """
    Load a PyTorch model from a local file or a run.

    :param model_uri: The location, in URI format, of the MLflow model, for example:

                      - ``/Users/me/path/to/local/model``
                      - ``relative/path/to/local/model``
                      - ``s3://my_bucket/path/to/model``
                      - ``runs:/<mlflow_run_id>/run-relative/path/to/model``
                      - ``models:/<model_name>/<model_version>``
                      - ``models:/<model_name>/<stage>``

                      For more information about supported URI schemes, see
                      `Referencing Artifacts <https://www.mlflow.org/docs/latest/concepts.html#
                      artifact-locations>`_.
    :param dst_path: The local filesystem path to which to download the model artifact.
                     This directory must already exist. If unspecified, a local output
                     path will be created.

    :param kwargs: kwargs to pass to ``torch.load`` method.
    :return: A PyTorch model.

    .. code-block:: python
        :caption: Example

        import torch
        import mlflow.pytorch

        # Class defined here
        class LinearNNModel(torch.nn.Module):
            ...

        # Initialize our model, criterion and optimizer
        ...

        # Training loop
        ...

        # Log the model
        with mlflow.start_run() as run:
            mlflow.hftransformers.log_model(model, "model", tokenizer)

        # Inference after loading the logged model
        model_uri = "runs:/{}/model".format(run.info.run_id)
        loaded_model, tokenizer = mlflow.hftransformers.load_model(model_uri)
        for x in [4.0, 6.0, 30.0]:
            X = torch.Tensor([[x]])
            y_pred = loaded_model(X)
            print("predict X: {}, y_pred: {:.2f}".format(x, y_pred.data.item()))

    .. code-block:: text
        :caption: Output

        predict X: 4.0, y_pred: 7.57
        predict X: 6.0, y_pred: 11.64
        predict X: 30.0, y_pred: 60.48
    """
    import transformers

    local_model_path = _download_artifact_from_uri(artifact_uri=model_uri, output_path=dst_path)
    hf_conf = _get_flavor_configuration(model_path=local_model_path, flavor_name=FLAVOR_NAME)
    _add_code_from_conf_to_system_path(local_model_path, hf_conf)

    if transformers.__version__ != hf_conf["transformers_version"]:
        _logger.warning(
            "Stored model version '%s' does not match installed transformers_version version '%s'",
            hf_conf["transformers_version"],
            transformers.__version__,
        )
    hf_model_artifacts_path = os.path.join(local_model_path, hf_conf["model_data"])
    return _load_model(path=hf_model_artifacts_path, hf_conf=hf_conf)


def load_pipeline(model_uri, dst_path=None, **kwargs):
    local_model_path = _download_artifact_from_uri(artifact_uri=model_uri, output_path=dst_path)
    hf_conf = _get_flavor_configuration(local_model_path, FLAVOR_NAME)
    hf_model_artifacts_path = os.path.join(local_model_path, hf_conf["model_data"])
    task_type, hf_model, tokenizer, config = _load_model(hf_model_artifacts_path, hf_conf)
    task_type = kwargs.pop("task_type", task_type)
    hf_conf["path"] = local_model_path
    return _HFPipelineWrapper(task_type, hf_model, tokenizer, config, hf_conf, **kwargs)


def _load_pyfunc(path, **kwargs):
    """
    Load PyFunc implementation. Called by ``pyfunc.load_model``.

    :param path: Local filesystem path to the MLflow Model with the ``pytorch`` flavor.
    """
    if "\\" in path:
        path1 = "\\".join(path.split("\\")[:-1])
    else:
        path1 = "/".join(path.split("/")[:-1])
    hf_conf = _get_flavor_configuration(path1, FLAVOR_NAME)
    task_type, hf_model, tokenizer, config = _load_model(path, hf_conf)
    hf_conf["path"] = path1
    return _HFTransformersWrapper(task_type, hf_model, tokenizer, config, hf_conf)


class _HFTransformersWrapper:
    """
    Wrapper class that creates a predict function such that
    predict(data: pd.DataFrame) -> model's output as pd.DataFrame (pandas DataFrame)
    """

    def __init__(self, task_type, hf_model, tokenizer, config, hf_conf):
        self.task_type = task_type
        self.hf_model = hf_model
        self.tokenizer = tokenizer
        self.config = config
        self.misc_conf = self._get_misc_conf(hf_conf)

    def _validate_data(self, data):
        if isinstance(data, dict):
            addn_args = data.pop("parameters", {})
            if "inputs" not in data:
                raise TypeError("Data dict must contain 'inputs' field")
            df = pd.DataFrame({key: data["inputs"][key] for key in data["inputs"]})
            return df, addn_args
        if isinstance(data, np.ndarray) and data.ndim > 2:
            raise TypeError("Number of Dimensions of ndarray should be < 3")
        if isinstance(data, (pd.DataFrame, pd.Series, np.ndarray)):
            return data, {}
        elif isinstance(data, (list, dict)):
            raise TypeError(
                "The HF flavor does not support List or Dict input types as of now."
                "Please use a pandas.DataFrame or a numpy.ndarray"
            )
        else:
            raise TypeError("Input data should be pandas.DataFrame or numpy.ndarray")

    def _get_misc_conf(self, conf):
        misc_conf = {}
        for key in conf:
            if isinstance(conf[key], dict) and "path_list" in conf[key]:
                misc_conf[key] = np.load(os.path.join(conf["path"], conf[key]["path_list"]), allow_pickle=True)
            elif key == "extra_files" and isinstance(conf[key], list):
                item_to_add = []
                for item in conf[key]:
                    if isinstance(item, dict) and "path" in item:
                        item_to_add.append({"path": os.path.join(conf["path"], item["path"])})
                misc_conf[key] = item_to_add
            else:
                misc_conf[key] = conf[key]
        return misc_conf

    def _get_problem_type(self, **kwargs):
        if kwargs.get("hf_predict_module", None) is not None:
            return Constants.HF_SCRIPT_BASED_PREDICTION
        if kwargs.get("multilabel", False):
            return Constants.MULTILABEL
        if hasattr(self.hf_model.config, "problem_type"):
            return self.hf_model.config.problem_type
        return None

    def predict(self, data):
        if hasattr(self.hf_model, 'eval'):
            self.hf_model.eval()
        from azureml.evaluate.mlflow.hftransformers._task_based_predictors import get_predictor
        data, addn_args = self._validate_data(data)
        self.task_type = addn_args.pop("task_type", self.task_type)
        problem_type = self._get_problem_type(**self.misc_conf)
        predictor_kwargs = {**self.misc_conf, **addn_args}
        predictor = get_predictor(self.task_type, problem_type)(task_type=self.task_type,
                                                                model=self.hf_model,
                                                                tokenizer=self.tokenizer,
                                                                config=self.config)
        return predictor.predict(data, **predictor_kwargs)


class _HFPipelineWrapper(_HFTransformersWrapper):
    """
    Wrapper class that creates a predict function such that
    predict(data: pd.DataFrame) -> model's output as pd.DataFrame (pandas DataFrame)
    """

    def __init__(self, task_type, hf_model, tokenizer, config, hf_conf, **kwargs):
        super().__init__(task_type, hf_model, tokenizer, config, hf_conf)
        self.pipeline_args = kwargs
        self.pipeline = pipeline(task_type, model=self.hf_model, tokenizer=self.tokenizer, **kwargs)

    def predict(self, data, **kwargs):
        if hasattr(self.hf_model, 'eval'):
            self.hf_model.eval()
        from azureml.evaluate.mlflow.hftransformers._task_based_pipeline_predictors import get_pipeline_predictor
        data, addn_args = self._validate_data(data)
        problem_type = self._get_problem_type(**self.misc_conf)
        predictor_kwargs = {**self.misc_conf, **kwargs, **addn_args}
        if "task_type" in predictor_kwargs:
            self.task_type = predictor_kwargs.pop("task_type")
            self.pipeline = pipeline(self.task_type, model=self.hf_model, tokenizer=self.tokenizer, **self.pipeline_args)
        predictor = get_pipeline_predictor(self.task_type, problem_type)(task_type=self.task_type, model=self.hf_model,
                                                                         tokenizer=self.tokenizer,
                                                                         config=self.config, pipeline_obj=self.pipeline)
        return predictor.predict(data, **predictor_kwargs)
