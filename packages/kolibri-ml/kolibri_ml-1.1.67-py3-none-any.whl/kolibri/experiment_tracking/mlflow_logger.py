import secrets
import os
import tempfile
import sklearn
import platform
try:
    from kolibri import mlflow as kolibri_flavor
except:
    pass
from kolibri import __version__
try:
    import mlflow
    import mlflow.sklearn
except ImportError:
    mlflow = None

def mlflow_remove_bad_chars(string: str) -> str:
    """Leaves only alphanumeric, spaces _, -, ., / in a string"""
    return "".join(c for c in string if c.isalpha() or c in ("_", "-", ".", " ", "/"))

SETUP_TAG = "Session Initialized"

class MlflowLogger():
    def __init__(self, config={}):
        if mlflow is None:
            raise ImportError(
                "MlflowLogger requires mlflow. Install using `pip install mlflow`"
            )
        if "MLFLOW_TRACKING_URI" in os.environ:
            self.traking_uri= os.environ["MLFLOW_TRACKING_URI"]
        if config["experiment-uri"] not in [None, ""]:
            self.traking_uri=config["experiment-uri"]

        self.experiment_name=config['experiment-name']
        if self.traking_uri is not None:
            mlflow.set_tracking_uri(self.traking_uri)

        self.run = None

    def init_experiment(self, exp_name_log):
        # get USI from nlp or tabular
        USI = secrets.token_hex(nbytes=2)

        experiment = mlflow.set_experiment(experiment_name=exp_name_log)

        self.run=mlflow.start_run(experiment_id=experiment.experiment_id)


    def finish_experiment(self):
        try:
            mlflow.end_run()
        except Exception:
            pass

    def log_params(self, params):
        params = {mlflow_remove_bad_chars(k): v for k, v in params.items()}
        mlflow.log_params(params)

    def log_metrics(self, metrics):
        mlflow.log_metrics(metrics)

    def set_tags(self, source, experiment_custom_tags, runtime, USI=None):
        # get USI from nlp or tabular
        if not USI:
            try:
                USI = secrets.token_hex(nbytes=2)
            except Exception:
                pass

        # Get active run to log as tag
        RunID = mlflow.active_run().info.run_id

        # set tag of compare_models
        mlflow.set_tag("Source", source)

        # set custom tags if applicable
        if isinstance(experiment_custom_tags, dict):
            mlflow.set_tags(experiment_custom_tags)

        URI = secrets.token_hex(nbytes=4)
        mlflow.set_tag("URI", URI)
        mlflow.set_tag("USI", USI)
        mlflow.set_tag("Run Time", runtime)
        mlflow.set_tag("Run ID", RunID)

        mlflow.set_tag("version.mlflow", mlflow.__version__)
        mlflow.set_tag("version.sklearn", sklearn.__version__)
        mlflow.set_tag("version.platform", platform.platform())
        mlflow.set_tag("version.python", platform.python_version())

    def log_artifact(self, file, type="artifact"):
        mlflow.log_artifact(file)

    def log_pandas(self, df, type="artifact"):

        with tempfile.TemporaryDirectory() as tmp_dir:

            file_path=os.path.join(tmp_dir, 'validatation_data_.xlsx')
            if df is not None:
                df.to_excel(file_path)
            self.log_artifact(file_path)

    def log_plot(self, plot, title=None):
        self.log_artifact(plot)

    def log_hpram_grid(self, html_file, title="hpram_grid"):
        self.log_artifact(html_file)

    def log_kolibri_pipeline(self, experiment):
        # get default conda env
        from mlflow.sklearn import get_default_conda_env

        default_conda_env = get_default_conda_env()
        default_conda_env["name"] = f"{experiment.experiment_name}-env"
        default_conda_env.get("dependencies").pop(-3)
        dependencies = default_conda_env.get("dependencies")[-1]

        dep = f"kolibri-ml=={__version__}"
        dependencies["pip"] = [dep]

        try:
            kolibri_flavor.log_model(experiment, artifact_path=experiment.config["artefacts-path"])
        except Exception as e:
            print(e)



    def register_model(self, registered_model_name, artifact_path, registered_model_version_stage="Staging", archive_existing_versions=True):
        if self.run is None:
            raise Exception("Cannot register model if experiment is not tracked.")
        client=None

        model_uri = "runs:/{run_id}/{artifact_path}".format(run_id=self.run.info.run_id, artifact_path=artifact_path)

        try:
            client = mlflow.client.MlflowClient(self.traking_uri)
            model_details = mlflow.register_model(model_uri=model_uri, name=registered_model_name)

        except Exception as e:
            print(e)
            pass

        source = f"{self.run.info.artifact_uri}/{registered_model_name}"
        print("Model source:",source)
#        version = client.create_model_version(registered_model_name, source, self.run.info.run_id)
        if registered_model_version_stage:
            client.transition_model_version_stage(registered_model_name, model_details.version, registered_model_version_stage, archive_existing_versions)
