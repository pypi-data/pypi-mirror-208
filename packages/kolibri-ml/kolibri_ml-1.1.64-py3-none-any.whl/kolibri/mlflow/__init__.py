import inspect
import os
import logging
import pickle
import yaml

from mlflow import pyfunc
from mlflow.exceptions import MlflowException
from mlflow.models import Model
from mlflow.models.model import MLMODEL_FILE_NAME
from mlflow.models.signature import ModelSignature
from mlflow.models.utils import ModelInputExample, _save_example
from mlflow.protos.databricks_pb2 import INVALID_PARAMETER_VALUE
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
from mlflow.utils.file_utils import write_to
import kolibri
from mlflow.utils.model_utils import (
    _get_flavor_configuration,
    _validate_and_copy_code_paths,
    _add_code_from_conf_to_system_path,
    _validate_and_prepare_target_save_path,
)
from mlflow.utils.autologging_utils import (
    _get_new_training_session_class,
)
from mlflow.tracking._model_registry import DEFAULT_AWAIT_MAX_SLEEP_SECONDS

FLAVOR_NAME = "kolibri"

SERIALIZATION_FORMAT_PICKLE = "pickle"
SERIALIZATION_FORMAT_CLOUDPICKLE = "cloudpickle"

SUPPORTED_SERIALIZATION_FORMATS = [SERIALIZATION_FORMAT_PICKLE, SERIALIZATION_FORMAT_CLOUDPICKLE]

_logger = logging.getLogger(__name__)
_SklearnTrainingSession = _get_new_training_session_class()


def get_default_pip_requirements():
    """
    :return: A list of default pip requirements for MLflow Models produced by this flavor.
             Calls to :func:`save_model()` and :func:`log_model()` produce a pip environment
             that, at minimum, contains these requirements.
    """
    pip_deps = [_get_pinned_requirement("kolibri-ml", module="kolibri")]

    return pip_deps


def get_default_conda_env(include_cloudpickle=False):
    """
    :return: The default Conda environment for MLflow Models produced by calls to
             :func:`save_model()` and :func:`log_model()`.
    """
    return _mlflow_conda_env(additional_pip_deps=get_default_pip_requirements())


def save_model(
    sk_model,
    path,
    conda_env=None,
    code_paths=None,
    mlflow_model=None,
    serialization_format=SERIALIZATION_FORMAT_CLOUDPICKLE,
    signature: ModelSignature = None,
    input_example: ModelInputExample = None,
    pip_requirements=None,
    extra_pip_requirements=None,
    pyfunc_predict_fn="predict",
    metadata=None,
):

    import kolibri

    _validate_env_arguments(conda_env, pip_requirements, extra_pip_requirements)

    if serialization_format not in SUPPORTED_SERIALIZATION_FORMATS:
        raise MlflowException(
            message=(
                f"Unrecognized serialization format: {serialization_format}. Please specify one"
                f" of the following supported formats: {SUPPORTED_SERIALIZATION_FORMATS}."
            ),
            error_code=INVALID_PARAMETER_VALUE,
        )

    _validate_and_prepare_target_save_path(path)
    code_path_subdir = _validate_and_copy_code_paths(code_paths, path)

    if mlflow_model is None:
        mlflow_model = Model()
    if signature is not None:
        mlflow_model.signature = signature
    if input_example is not None:
        _save_example(mlflow_model, input_example, path)
    if metadata is not None:
        mlflow_model.metadata = metadata

    model_data_subpath = "model.pkl"
    model_data_path = os.path.join(path, model_data_subpath)
    sk_model.persist(model_data_path, "")


    pyfunc.add_to_model(
            mlflow_model,
            loader_module="kolibri.mlflow",
            model_path=model_data_subpath,
            conda_env=_CONDA_ENV_FILE_NAME,
            python_env=_PYTHON_ENV_FILE_NAME,
            code=code_path_subdir,
            predict_fn=pyfunc_predict_fn,
        )

    mlflow_model.add_flavor(
        FLAVOR_NAME,
        pickled_model=model_data_subpath,
        kolibri_version=kolibri.__version__,
        serialization_format=serialization_format,
        code=code_path_subdir,
    )
    mlflow_model.save(os.path.join(path, MLMODEL_FILE_NAME))

    if conda_env is None:
        if pip_requirements is None:
            default_reqs = get_default_pip_requirements()
        else:
            default_reqs = None
        conda_env, pip_requirements, pip_constraints = _process_pip_requirements(
            default_reqs,
            pip_requirements,
            extra_pip_requirements,
        )
    else:
        conda_env, pip_requirements, pip_constraints = _process_conda_env(conda_env)

    with open(os.path.join(path, _CONDA_ENV_FILE_NAME), "w") as f:
        yaml.safe_dump(conda_env, stream=f, default_flow_style=False)

    # Save `constraints.txt` if necessary
    if pip_constraints:
        write_to(os.path.join(path, _CONSTRAINTS_FILE_NAME), "\n".join(pip_constraints))

    # Save `requirements.txt`
    write_to(os.path.join(path, _REQUIREMENTS_FILE_NAME), "\n".join(pip_requirements))

    _PythonEnv.current().to_yaml(os.path.join(path, _PYTHON_ENV_FILE_NAME))


def log_model(
    sk_model,
    artifact_path,
    conda_env=None,
    code_paths=None,
    serialization_format=SERIALIZATION_FORMAT_CLOUDPICKLE,
    registered_model_name=None,
    signature: ModelSignature = None,
    input_example: ModelInputExample = None,
    await_registration_for=DEFAULT_AWAIT_MAX_SLEEP_SECONDS,
    pip_requirements=None,
    extra_pip_requirements=None,
    pyfunc_predict_fn="predict",
    metadata=None,
):

    return Model.log(
        artifact_path=artifact_path,
        flavor=kolibri.mlflow,
        sk_model=sk_model,
        conda_env=conda_env,
        code_paths=code_paths,
        serialization_format=serialization_format,
        registered_model_name=registered_model_name,
        signature=signature,
        input_example=input_example,
        await_registration_for=await_registration_for,
        pip_requirements=pip_requirements,
        extra_pip_requirements=extra_pip_requirements,
        pyfunc_predict_fn=pyfunc_predict_fn,
        metadata=metadata,
    )


def _load_model_from_local_file(path):
    """Load a kolibri model saved as an MLflow artifact on the local file system.
    :param path: Local filesystem path to the MLflow Model saved with the ``kolibri`` flavor
    :param serialization_format:.
    """
    from kolibri import ModelLoader

    return ModelLoader.load(path)


def _load_pyfunc(path):
    """
    Load PyFunc implementation. Called by ``pyfunc.load_model``.
    :param path: Local filesystem path to the MLflow Model with the `` kolibri`` flavor.
    """
    if os.path.isfile(path):
        # Scikit-learn models saved in older versions of MLflow (<= 1.9.1) specify the ``data``
        # field within the pyfunc flavor configuration. For these older models, the ``path``
        # parameter of ``_load_pyfunc()`` refers directly to a serialized scikit-learn model
        # object. In this case, we assume that the serialization format is ``pickle``, since
        # the model loading procedure in older versions of MLflow used ``pickle.load()``.
        serialization_format = SERIALIZATION_FORMAT_PICKLE
    else:
        # In contrast, scikit-learn models saved in versions of MLflow > 1.9.1 do not
        # specify the ``data`` field within the pyfunc flavor configuration. For these newer
        # models, the ``path`` parameter of ``load_pyfunc()`` refers to the top-level MLflow
        # Model directory. In this case, we parse the model path from the MLmodel's pyfunc
        # flavor configuration and attempt to fetch the serialization format from the
        # scikit-learn flavor configuration
        try:
            kolibri_flavor_conf = _get_flavor_configuration(
                model_path=path, flavor_name=FLAVOR_NAME)
            serialization_format = kolibri_flavor_conf.get(
                "serialization_format", SERIALIZATION_FORMAT_PICKLE
            )
        except Exception:
            _logger.warning(
                "Could not find scikit-learn flavor configuration during model loading process."
                " Assuming 'pickle' serialization format."
            )
            serialization_format = SERIALIZATION_FORMAT_PICKLE

        pyfunc_flavor_conf = _get_flavor_configuration(
            model_path=path, flavor_name=pyfunc.FLAVOR_NAME
        )
        path = os.path.join(path, pyfunc_flavor_conf["model_path"])

    return _load_model_from_local_file(path=path)


class _SklearnCustomModelPicklingError(pickle.PicklingError):
    """
    Exception for describing error raised during pickling custom  kolibri estimator
    """

    def __init__(self, sk_model, original_exception):
        """
        :param sk_model: The custom  kolibri model to be pickled
        :param original_exception: The original exception raised
        """
        super().__init__(
            f"Pickling custom  kolibri model {sk_model.__class__.__name__} failed "
            f"when saving model: {str(original_exception)}"
        )
        self.original_exception = original_exception


def load_model(model_uri, dst_path=None):
    """
    Load a kolibri-ml model from a local file or a run.
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
    :return: A kolibri-ml model.
    .. code-block:: python
        :caption: Example

    """
    local_model_path = _download_artifact_from_uri(artifact_uri=model_uri, output_path=dst_path)
    flavor_conf = _get_flavor_configuration(model_path=local_model_path, flavor_name=FLAVOR_NAME)
    _add_code_from_conf_to_system_path(local_model_path, flavor_conf)
    kolibri_model_artifacts_path = os.path.join(local_model_path, flavor_conf["pickled_model"])
    return _load_model_from_local_file(
        path= kolibri_model_artifacts_path
)




def autolog(
    log_input_examples=False,
    log_model_signatures=True,
    log_models=True,
    disable=False,
    exclusive=False,
    disable_for_unsupported_versions=False,
    silent=False,
    max_tuning_runs=5,
    log_post_training_metrics=True,
    serialization_format=SERIALIZATION_FORMAT_CLOUDPICKLE,
    registered_model_name=None,
    pos_label=None,
):  # pylint: disable=unused-argument


    raise NotImplementedError