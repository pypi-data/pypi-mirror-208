# encoding: utf-8



# file: __init__.py
# time: 11:22 上午

import warnings
import tensorflow as tf
from typing import TYPE_CHECKING, Union
from tensorflow.keras.utils import CustomObjectScope

from kolibri.backend.tensorflow  import custom_objects
from .data import get_list_subset
from .data import unison_shuffled_copies
from .multi_label import MultiLabelBinarizer
from .serialize import load_data_object
from .model import convert_to_saved_model

if TYPE_CHECKING:
    from kolibri.backend.tensorflow.tasks.text.labeling import BaseLabelingModel
    from kolibri.backend.tensorflow.tasks.text.classification import BaseTextClassificationModel


def custom_object_scope() -> CustomObjectScope:
    return tf.keras.utils.custom_object_scope(custom_objects)


def load_model(model_path: str) -> Union["BaseLabelingModel", "BaseTextClassificationModel"]:
    warnings.warn("The 'load_model' function is deprecated, "
                  "use 'XX_Model.load_model' instead", DeprecationWarning, 2)
    from kolibri.backend.tensorflow.tasks.base_model import TaskBaseModel
    return TaskBaseModel.load_model(model_path=model_path)


if __name__ == "__main__":
    pass
