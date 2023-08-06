from kolibri.autolearn.model_zoo.zoo_estimator import ZooEstimator
from copy import deepcopy
from kolibri.model_trainer import ModelTrainer, ModelConfig
from IPython.display import display, clear_output
from kdmt.jupyter import isnotebook
import pandas as pd
import ipywidgets as ipw
from kolibri.datasets import get_data

from kolibri.formers.text.classifier import TextClassiFormer
import warnings

warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')


def _build_model_pipeline(config, data, content, target, progress=None, verbose=True):
    trainer = ModelTrainer(ModelConfig(config))

    if progress and verbose:
        progress.value += 1
        progress.description = "Fitting model"
        clear_output()
        display(progress)

    _data_x_train, _data_y_train, _data_x_test, _data_y_test = preprocessing_pipeline = trainer.fit_transformers(
        [v for v in data[content].values if v is not None],
        [v for v in data[target].values if v is not None])

    _model = trainer.fit_estimator(_data_x_train, _data_y_train, _data_x_test)

    return _model.scores


__default_configs = {
    "track-experiments": False,
    'experiment-name': 'compare_models',
    'language': "en",
    'do-lower-case': True,
    "model": None,
    "evaluate-performance": False,
    'output-folder': '.',
    'pipeline': ['WordTokenizer', 'CollocationAnalyzer', 'TFIDFFeaturizer', 'ZooEstimator'],
    "remove-stopwords": True
}


def compare_models(data, content, target, config={}):
    configs = deepcopy(__default_configs)

    configs.update(config)

    verbose = isnotebook()
    progress = None
    if data is not None:
        if not isinstance(data, pd.DataFrame):
            raise ValueError("data parameter should be a pandas Dataframe")
        if target not in list(data.columns):
            raise ValueError("target: " + target + " not in the provided Dataframe")

        print("Preparing display monitor")

        if verbose:
            progress = ipw.IntProgress(
                value=0, min=0, max=4, step=1, description="Initialuzing: "
            )

            clear_output()
            display(progress)

        scores = _build_model_pipeline(configs, data=data, content=content, target=target, progress=progress)
        return scores

def create_model(data, content, target,  model, configs={}):
    configs["model"]=model
    return TextClassiFormer( output_folder='.', data=data, content=content, target=target, configs=configs)

if __name__ == "__main__":
    data = get_data('spam')
    #compare_models(data, content="text", target="label")
    model=create_model(data=data, content="text", target="label", model="LogisticRegression")
    model.plot()