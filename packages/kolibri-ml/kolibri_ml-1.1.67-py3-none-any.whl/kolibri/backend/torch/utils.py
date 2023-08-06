
from os.path import exists, join
import torch


FILE_ARGUMENTS = "arguments.json"
FILE_MODEL = "model.pth"


def running_device(device):
    return device if device else torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def model_filepath(model_dir):
    return join(model_dir, FILE_MODEL)