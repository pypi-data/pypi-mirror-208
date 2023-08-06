
from  kdmt.jupyter import isnotebook
from kolibri.config import ModelConfig
from kolibri.model_loader import ModelLoader
from kolibri.model_trainer import ModelTrainer
from kolibri.stopwords import get_stop_words
import os

import pandas as pd

from kolibri.logger import get_logger
import ipywidgets as ipw
from IPython.display import display, clear_output

logger=get_logger(__name__)


class TextClassiFormer():
    """
    Text classification pipeline

    """

    defaults={
        'track-experiments': False,
        'experiment-name':'experiment_1',
        'language': 'en',
        'do-lower-case':True,
        "evaluate-performance": True,
        "model": 'LogisticRegression',
        "remove-stopwords": True,
        "model_name": "classifier_file"
    }
    def __init__(self,output_folder, data, content, target, configs={}):

        for key in configs:
            if key not in self.defaults:
                self.defaults[key]=configs[key]

        self.verbose=isnotebook()
        progress=None
        if data is not None:
            if not isinstance(data, pd.DataFrame):
                raise ValueError("data parameter should be a pandas Dataframe")
            if target not in list(data.columns):
                raise ValueError("target: "+ target+" not in the provided Dataframe")
            self.target=target
            self.content=content

            logger.info("Preparing display monitor")

            if self.verbose:
                progress = ipw.IntProgress(
                    value=0, min=0, max=4, step=1, description="Initialuzing: "
                )

                clear_output()
                display(progress)

            self.data=data
            self.defaults.update(configs)

            self.trainer=self._build(output_folder, progress)
            if self.verbose:
                clear_output()
                progress.value+=1
                progress.description="Saving Model"
                display(progress)
            model_directory = self.trainer.persist(output_folder, fixed_model_name=self.defaults["model_name"])
            if self.verbose:
                clear_output()
                progress.value+=1
                progress.description="Loading Model"
                display(progress)
            self.model_interpreter = ModelLoader.load(os.path.join(output_folder, self.defaults["model_name"]))
            if self.verbose:
                clear_output()
                progress.value+=1
                progress.description="Finished"
                display(progress)

    def __call__(self, data, target=None):

        res= self.model_interpreter.predict(data)

        res=pd.DataFrame(res).fillna(0)
        return res

    def _build(self, output_folder, progress=None):
        config = {}

        config['track-experiments'] = self.defaults['track-experiments']
        config['experiment-name'] = self.defaults['experiment-name']
        config['language'] = self.defaults['language']
        config['do-lower-case'] = self.defaults['do-lower-case']
        config["model"] = self.defaults["model"]
        config["evaluate-performance"] = self.defaults["evaluate-performance"]
        config['output-folder'] = output_folder
        config['pipeline'] = ['WordTokenizer', 'CollocationAnalyzer','TFIDFFeaturizer', 'SklearnEstimator']

        config["remove-stopwords"] = self.defaults["remove-stopwords"]
        for key in self.defaults:
            if key not in config:
                config[key]=self.defaults[key]

        trainer = ModelTrainer(ModelConfig(config))

        if progress and self.verbose:
            progress.value += 1
            progress.description = "Fitting model"
            clear_output()
            display(progress)
        self._data_x_train, self._data_y_train,self._data_x_test, self._data_y_test=self.preprocessing_pipeline=trainer.fit_transformers([v for v in self.data[self.content].values if v is not None], [v for v in self.data[self.target].values if v is not None])

        self._model=trainer.fit_estimator(self._data_x_train, self._data_y_train,self._data_x_test)

        return trainer





if __name__=="__main__":
    from kolibri.datasets import get_data

    data=get_data('spam')
    classification_former=TextClassiFormer(".", data, "text", "label")
