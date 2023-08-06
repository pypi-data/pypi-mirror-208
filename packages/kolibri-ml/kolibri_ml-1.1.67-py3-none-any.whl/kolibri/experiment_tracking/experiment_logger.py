import gc
import os
import tempfile
import traceback
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import numpy as np
import pandas as pd

from kolibri.experiment_tracking.mlflow_logger import SETUP_TAG

def get_pipeline_estimator_label(pipeline) -> str:
    try:
        model_step = pipeline.steps[-1]
    except Exception:
        return ""

    return model_step[0]



class ExperimentLogger:
    def __init__(self, logger_list):
        self.loggers = logger_list

    def __repr__(self) -> str:
        return ", ".join([str(logger) for logger in self.loggers])

    def init_loggers(self, exp_name_log):
        for logger in self.loggers:
            logger.init_experiment(exp_name_log)

    def log_params(self, params):
        for logger in self.loggers:
            logger.log_params(params)

    def log_model(
        self,
        experiment: "ML_Experiment",
        model,
        model_results,
        pipeline,
        score_dict: dict,
        source: str,
        runtime: float,
        model_fit_time: float,
        dataframes=[],
        log_plots: Optional[List[str]] = None,
        experiment_custom_tags: Optional[Dict[str, Any]] = None,
        tune_cv_results=None,
        URI=None,
        display=None,
    ):
        log_plots = log_plots or []
        console = experiment.logger
        console.info("Creating Dashboard logs")

        # Creating Logs message monitor
        if display:
            display.update_monitor(1, "Creating Logs")

        self.init_loggers(experiment.experiment_name)

        # Log model parameters
        pipeline_estimator_name = get_pipeline_estimator_label(model)
        if pipeline_estimator_name:
            params = model.named_steps[pipeline_estimator_name]
        else:
            params = model

        # get regressor from meta estimator
#        params = get_estimator_from_meta_estimator(params)

        try:
            try:
                params = params.estimator.model.get_all_params()
            except AttributeError:
                params = params.estimator.model.get_params()
        except Exception:
            console.warning(
                f"Couldn't get params for model. Exception:\n{traceback.format_exc()}"
            )
            params = {}

        for i in list(params):
            v = params.get(i)
            if len(str(v)) > 250:
                params.pop(i)

        console.info(f"Logged params: {params}")
        score_dict["TT"] = model_fit_time

        # Log metrics
        def try_make_float(val):
            try:
                return np.float64(val)
            except Exception:
                return np.nan

        score_dict = {k: try_make_float(v) for k, v in score_dict.items()}

        for logger in self.loggers:
            logger.log_params(params)
            logger.log_metrics(score_dict)
            logger.set_tags(source, experiment_custom_tags, runtime, USI=None)

            with tempfile.TemporaryDirectory() as tmpdir:
                # Log the CV results as model_results.html artifact
                if dataframes:
                    for df in dataframes:
                        logger.log_pandas(df)

                if True:
                    results_path = os.path.join(tmpdir, "Results.html")
                    try:
                        model_results.data.to_html(
                            results_path, col_space=65, justify="left"
                        )
                    except Exception:
                        model_results.to_html(results_path, col_space=65, justify="left")
                    logger.log_artifact(results_path, "Results")


                # Log AUC and Confusion Matrix plot

                if log_plots:
                    console.info(
                        "SubProcess plot_model() called =================================="
                    )

                    def _log_plot(plot):
                        try:
                            plot_name = os.path.join(experiment.config["output-folder"], "plots", plot+".png")
                            if os.path.exists(plot_name):
                                logger.log_plot(plot_name, Path(plot_name).stem)

                        except Exception:
                            console.warning(
                                f"Couldn't create plot {plot} for model, exception below:\n"
                                f"{traceback.format_exc()}"
                            )
                    for plot in log_plots:
                        _log_plot(plot)

                    console.info(
                        "SubProcess plot_model() end =================================="
                    )

                # Log hyperparameter tuning grid
                if tune_cv_results:
                    iterations_path = os.path.join(tmpdir, "Iterations.html")
                    d1 = tune_cv_results.get("params")
                    dd = pd.DataFrame.from_dict(d1)
                    dd["Score"] = tune_cv_results.get("mean_test_score")
                    dd.to_html(iterations_path, col_space=75, justify="left")
                    logger.log_hpram_grid(iterations_path, "Hyperparameter-grid")


                logger.log_kolibri_pipeline(experiment)


        self.finish()
        gc.collect()


    def log_artifact(self, artifact, message):
        for logger in self.loggers:
            logger.log_artifact(artifact, message)

    def register_model(self, registered_model_name, artifact, registered_model_version_stage="Staging", archive_existing_versions=True):
        for logger in self.loggers:
            logger.register_model(registered_model_name, artifact, registered_model_version_stage=registered_model_version_stage, archive_existing_versions=archive_existing_versions)
    def log_pandas(self, df):
        for logger in self.loggers:
            logger.log_pandas(df)

    def log_model_comparison(self, results, source):
        for logger in self.loggers:
            logger.log_model_comparison(results, source)

    def finish(self):
        for logger in self.loggers:
            logger.finish_experiment()
