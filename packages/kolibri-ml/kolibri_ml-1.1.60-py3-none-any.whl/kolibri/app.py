from typing import Any, Dict, List, Optional, Union
from kolibri.model_trainer import ModelTrainer, ModelConfig
from kolibri.model_loader import ModelLoader
import pandas as pd
import os


def create_model(X, y, configs, persist=True, tune=False):

    """
    This function trains and evaluates the performance of a given estimator
    using cross validation. The output of this function is a score grid with
    CV scores by fold. Metrics evaluated during CV can be accessed using the
    ``get_metrics`` function. Custom metrics can be added or removed using
    ``add_metric`` and ``remove_metric`` function. All the available models
    can be accessed using the ``models`` function.

    Example
    -------
    >>> from kolibri.datasets import get_data
    >>> juice = get_data('juice')
    >>> from kolibri.task.text.classification import *
    >>> lr = create_model('lr')


    estimator: str or scikit-learn compatible object
        ID of an estimator available in model library or pass an untrained
        model object consistent with scikit-learn API. Estimators available
        in the model library (ID - Name):

        * 'lr' - Logistic Regression
        * 'knn' - K Neighbors Classifier
        * 'nb' - Naive Bayes
        * 'dt' - Decision Tree Classifier
        * 'svm' - SVM - Linear Kernel
        * 'rbfsvm' - SVM - Radial Kernel
        * 'gpc' - Gaussian Process Classifier
        * 'mlp' - MLP Classifier
        * 'ridge' - Ridge Classifier
        * 'rf' - Random Forest Classifier
        * 'qda' - Quadratic Discriminant Analysis
        * 'ada' - Ada Boost Classifier
        * 'gbc' - Gradient Boosting Classifier
        * 'lda' - Linear Discriminant Analysis
        * 'et' - Extra Trees Classifier
        * 'xgboost' - Extreme Gradient Boosting
        * 'lightgbm' - Light Gradient Boosting Machine
        * 'catboost' - CatBoost Classifier


    fold: int or scikit-learn compatible CV generator, default = None
        Controls cross-validation. If None, the CV generator in the ``fold_strategy``
        parameter of the ``setup`` function is used. When an integer is passed,
        it is interpreted as the 'n_splits' parameter of the CV generator in the
        ``setup`` function.


    round: int, default = 4
        Number of decimal places the metrics in the score grid will be rounded to.


    cross_validation: bool, default = True
        When set to False, metrics are evaluated on holdout set. ``fold`` param
        is ignored when cross_validation is set to False.


    fit_kwargs: dict, default = {} (empty dict)
        Dictionary of arguments passed to the fit method of the model.


    groups: str or array-like, with shape (n_samples,), default = None
        Optional group labels when GroupKFold is used for the cross validation.
        It takes an array with shape (n_samples, ) where n_samples is the number
        of rows in training dataset. When string is passed, it is interpreted as
        the column name in the dataset containing group labels.


    probability_threshold: float, default = None
        Threshold for converting predicted probability to class label.
        It defaults to 0.5 for all classifiers unless explicitly defined
        in this parameter. Only applicable for binary classification.


    experiment_custom_tags: dict, default = None
        Dictionary of tag_name: String -> value: (String, but will be string-ified
        if not) passed to the mlflow.set_tags to add new custom tags for the experiment.


    verbose: bool, default = True
        Score grid is not printed when verbose is set to False.


    engine: Optional[str] = None
        The execution engine to use for the model, e.g. for Logistic Regression ("lr"), users can
        switch between "sklearn" and "sklearnex" by specifying
        `engine="sklearnex"`.


    return_train_score: bool, default = False
        If False, returns the CV Validation scores only.
        If True, returns the CV training scores along with the CV validation scores.
        This is useful when the user wants to do bias-variance tradeoff. A high CV
        training score with a low corresponding CV validation score indicates overfitting.


    **kwargs:
        Additional keyword arguments to pass to the estimator.


    Returns:
        Trained Model


    Warnings
    --------
    - AUC for estimators that does not support 'predict_proba' is shown as 0.0000.

    - Models are not logged on the ``MLFlow`` server when ``cross_validation`` param
      is set to False.

    """

    trainer = ModelTrainer(ModelConfig(configs))

    trainer.fit(X, y)
    #   trainer.pipeline.estimator.explain()

    if persist:
        model_directory = trainer.persist(configs['output-folder'], fixed_model_name="current")

    model_interpreter = ModelLoader.load(
        os.path.join(configs['output-folder'], 'current'))

    return model_interpreter



def optimize_threshold(
    estimator,
    optimize: str = "Accuracy",
    grid_interval: float = 0.1,
    return_data: bool = False,
    plot_kwargs: Optional[dict] = None,
):

    """
    This function optimizes probability threshold for a trained classifier. It
    iterates over performance metrics at different ``probability_threshold`` with
    a step size defined in ``grid_interval`` parameter. This function will display
    a plot of the performance metrics at each probability threshold and returns the
    best model based on the metric defined under ``optimize`` parameter.


    Example
    -------
    >>> from kolibri.datasets import get_data
    >>> juice = get_data('juice')
    >>> experiment_name = setup(data = juice,  target = 'Purchase')
    >>> lr = create_model('lr')
    >>> best_lr_threshold = optimize_threshold(lr)


    Parameters
    ----------
    estimator : object
        A trained model object should be passed as an estimator.


    optimize : str, default = 'Accuracy'
        Metric to be used for selecting best model.


    grid_interval : float, default = 0.0001
        Grid interval for threshold grid search. Default 10 iterations.


    return_data :  bool, default = False
        When set to True, data used for visualization is also returned.


    plot_kwargs :  dict, default = {} (empty dict)
        Dictionary of arguments passed to the visualizer class.


    Returns
    -------
    Trained Model


    Warnings
    --------
    - This function does not support multiclass classification problems.
    """

    return _CURRENT_EXPERIMENT.optimize_threshold(
        estimator=estimator,
        optimize=optimize,
        grid_interval=grid_interval,
        return_data=return_data,
        plot_kwargs=plot_kwargs,
    )




def deploy_model(
    model,
    model_name: str,
    authentication: dict,
    platform: str = "aws",
):
    """
    This function deploys the transformation pipeline and trained model on cloud.


    Example
    -------
    >>> from kolibri.datasets import get_data
    >>> juice = get_data('juice')
    >>> from kolibri.classification import *
    >>> exp_name = setup(data = juice,  target = 'Purchase')
    >>> lr = create_model('lr')
    >>> # sets appropriate credentials for the platform as environment variables
    >>> import os
    >>> os.environ["AWS_ACCESS_KEY_ID"] = str("foo")
    >>> os.environ["AWS_SECRET_ACCESS_KEY"] = str("bar")
    >>> deploy_model(model = lr, model_name = 'lr-for-deployment', platform = 'aws', authentication = {'bucket' : 'S3-bucket-name'})


    Amazon Web Service (AWS) users:
        To deploy a model on AWS S3 ('aws'), the credentials have to be passed. The easiest way is to use environment
        variables in your local environment. Following information from the IAM portal of amazon console account
        are required:

        - AWS Access Key ID
        - AWS Secret Key Access

        More info: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#environment-variables


    Google Cloud Platform (GCP) users:
        To deploy a model on Google Cloud Platform ('gcp'), project must be created
        using command line or GCP console. Once project is created, you must create
        a service account and download the service account key as a JSON file to set
        environment variables in your local environment.

        More info: https://cloud.google.com/docs/authentication/production


    Microsoft Azure (Azure) users:
        To deploy a model on Microsoft Azure ('azure'), environment variables for connection
        string must be set in your local environment. Go to settings of storage account on
        Azure portal to access the connection string required.

        - AZURE_STORAGE_CONNECTION_STRING (required as environment variable)

        More info: https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python?toc=%2Fpython%2Fazure%2FTOC.json


    model: scikit-learn compatible object
        Trained model object


    model_name: str
        Name of model.


    authentication: dict
        Dictionary of applicable authentication tokens.

        When platform = 'aws':
        {'bucket' : 'S3-bucket-name', 'path': (optional) folder name under the bucket}

        When platform = 'gcp':
        {'project': 'gcp-project-name', 'bucket' : 'gcp-bucket-name'}

        When platform = 'azure':
        {'container': 'azure-container-name'}


    platform: str, default = 'aws'
        Name of the platform. Currently supported platforms: 'aws', 'gcp' and 'azure'.


    Returns:
        None

    """

    return _CURRENT_EXPERIMENT.deploy_model(
        model=model,
        model_name=model_name,
        authentication=authentication,
        platform=platform,
    )




def convert_model(estimator, language: str = "python") -> str:

    """
    This function transpiles trained machine learning models into native
    inference script in different programming languages (Python, C, Java,
    Go, JavaScript, Visual Basic, C#, PowerShell, R, PHP, Dart, Haskell,
    Ruby, F#). This functionality is very useful if you want to deploy models
    into environments where you can't install your normal Python stack to
    support model inference.


    Example
    -------
    >>> from kolibri.datasets import get_data
    >>> juice = get_data('juice')
    >>> from kolibri.classification import *
    >>> exp_name = setup(data = juice,  target = 'Purchase')
    >>> lr = create_model('lr')
    >>> lr_java = convert_model(lr, 'java')


    estimator: scikit-learn compatible object
        Trained model object


    language: str, default = 'python'
        Language in which inference script to be generated. Following
        options are available:

        * 'python'
        * 'java'
        * 'javascript'
        * 'c'
        * 'c#'
        * 'f#'
        * 'go'
        * 'haskell'
        * 'php'
        * 'powershell'
        * 'r'
        * 'ruby'
        * 'vb'
        * 'dart'


    Returns:
        str

    """
    return _CURRENT_EXPERIMENT.convert_model(estimator, language)



def eda(display_format: str = "bokeh", **kwargs):

    """
    This function generates AutoEDA using AutoVIZ library. You must
    install Autoviz separately ``pip install autoviz`` to use this
    function.


    Example
    -------
    >>> from kolibri.datasets import get_data
    >>> juice = get_data('juice')
    >>> from kolibri.classification import *
    >>> exp_name = setup(data = juice,  target = 'Purchase')
    >>> eda(display_format = 'bokeh')

    display_format: str, default = 'bokeh'
        When set to 'bokeh' the plots are interactive. Other option is ``svg`` for static
        plots that are generated using matplotlib and seaborn.


    **kwargs:
        Additional keyword arguments to pass to the AutoVIZ class.


    Returns:
        None
    """
    return _CURRENT_EXPERIMENT.eda(display_format=display_format, **kwargs)



def check_fairness(estimator, sensitive_features: list, plot_kwargs: dict = {}):

    """
    There are many approaches to conceptualizing fairness. This function follows
    the approach known as group fairness, which asks: Which groups of individuals
    are at risk for experiencing harms. This function provides fairness-related
    metrics between different groups (also called subpopulation).


    Example
    -------
    >>> from kolibri.datasets import get_data
    >>> income = get_data('income')
    >>> from kolibri.classification import *
    >>> exp_name = setup(data = income,  target = 'income >50K')
    >>> lr = create_model('lr')
    >>> lr_fairness = check_fairness(lr, sensitive_features = ['sex', 'race'])


    estimator: scikit-learn compatible object
        Trained model object


    sensitive_features: list
        List of column names as present in the original dataset before any
        transformations.


    plot_kwargs: dict, default = {} (empty dict)
        Dictionary of arguments passed to the matplotlib plot.


    Returns:
        pandas.DataFrame

    """
    return _CURRENT_EXPERIMENT.check_fairness(
        estimator=estimator,
        sensitive_features=sensitive_features,
        plot_kwargs=plot_kwargs,
    )



def create_api(
    estimator, api_name: str, host: str = "127.0.0.1", port: int = 8000
) -> None:

    """
    This function takes an input ``estimator`` and creates a POST API for
    inference. It only creates the API and doesn't run it automatically.
    To run the API, you must run the Python file using ``!python``.


    Example
    -------
    >>> from kolibri.datasets import get_data
    >>> juice = get_data('juice')
    >>> from kolibri.classification import *
    >>> exp_name = setup(data = juice,  target = 'Purchase')
    >>> lr = create_model('lr')
    >>> create_api(lr, 'lr_api'
    >>> !python lr_api.py


    estimator: scikit-learn compatible object
        Trained model object


    api_name: scikit-learn compatible object
        Trained model object


    host: str, default = '127.0.0.1'
        API host address.


    port: int, default = 8000
        port for API.


    Returns:
        None
    """
    return _CURRENT_EXPERIMENT.create_api(
        estimator=estimator, api_name=api_name, host=host, port=port
    )



def create_docker(
    api_name: str, base_image: str = "python:3.8-slim", expose_port: int = 8000
) -> None:

    """
    This function creates a ``Dockerfile`` and ``requirements.txt`` for
    productionalizing API end-point.


    Example
    -------
    >>> from kolibri.datasets import get_data
    >>> juice = get_data('juice')
    >>> from kolibri.classification import *
    >>> exp_name = setup(data = juice,  target = 'Purchase')
    >>> lr = create_model('lr')
    >>> create_api(lr, 'lr_api')
    >>> create_docker('lr_api')


    api_name: str
        Name of API. Must be saved as a .py file in the same folder.


    base_image: str, default = "python:3.8-slim"
        Name of the base image for Dockerfile.


    expose_port: int, default = 8000
        port for expose for API in the Dockerfile.


    Returns:
        None
    """
    return _CURRENT_EXPERIMENT.create_docker(
        api_name=api_name, base_image=base_image, expose_port=expose_port
    )



def create_app(estimator, app_kwargs: Optional[dict] = None) -> None:

    """
    This function creates a basic gradio app for inference.
    It will later be expanded for other app types such as
    Streamlit.


    Example
    -------
    >>> from kolibri.datasets import get_data
    >>> juice = get_data('juice')
    >>> from kolibri.classification import *
    >>> exp_name = setup(data = juice,  target = 'Purchase')
    >>> lr = create_model('lr')
    >>> create_app(lr)


    estimator: scikit-learn compatible object
        Trained model object


    app_kwargs: dict, default = {} (empty dict)
        arguments to be passed to app class.


    Returns:
        None
    """
    return _CURRENT_EXPERIMENT.create_app(estimator=estimator, app_kwargs=app_kwargs)



def deep_check(estimator, check_kwargs: Optional[dict] = None) -> None:
    """
    This function runs a full suite check over a trained model
    using deepchecks library.


    Example
    -------
    >>> from kolibri.datasets import get_data
    >>> juice = get_data('juice')
    >>> from kolibri.classification import *
    >>> exp_name = setup(data = juice,  target = 'Purchase')
    >>> lr = create_model('lr')
    >>> deep_check(lr)


    estimator: scikit-learn compatible object
        Trained model object


    check_kwargs: dict, default = {} (empty dict)
        arguments to be passed to deepchecks full_suite class.


    Returns:
        Results of deepchecks.suites.full_suite.run
    """
    return _CURRENT_EXPERIMENT.deep_check(
        estimator=estimator, check_kwargs=check_kwargs
    )

