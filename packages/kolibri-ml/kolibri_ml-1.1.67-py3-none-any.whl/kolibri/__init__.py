import sys

sys.path.append("..")
sys.path.append(".")
sys.path.append("../..")


"""
The Kolibri toolkit is an open source Python library
for Artificial Intelligence including Natural Language Processing and general purpose Machine learning with Scikit learn and Deep learning.  

Mohamed Ben Hadou (2017).
isort:skip_file
"""

import os

# //////////////////////////////////////////////////////
# Metadata
# //////////////////////////////////////////////////////

# Version.  For each new release, the version number should be updated
# in the file VERSION.
try:
    # If a VERSION file exists, use it!
    version_file = os.path.join(os.path.dirname(__file__), "VERSION")
    with open(version_file) as infile:
        __version__ = infile.read().strip()
except NameError:
    __version__ = "unknown (running code interactively?)"
except OSError as ex:
    __version__ = "unknown (%s)" % ex

if __doc__ is not None:  # fix for the ``python -OO``
    __doc__ += "\n@version: " + __version__


# Copyright notice
__copyright__ = """\
Copyright (C) 2017-2022 Mentis Consulting.

Distributed and Licensed under the Apache License, Version 2.0,
which is included by reference.
"""

__license__ = "Apache License, Version 2.0"
# Description of the toolkit, keywords, and the project's primary URL.
__longdescr__ = """\
  Kolibri is a Python package for Artificial Intelligence.  Kolibri requires Python 3.7, 3.8, 3.9 or 3.10."""
__keywords__ = [
    "NLP",
    "CL",
    "natural language processing",
    "parsing",
    "tagging",
    "tokenizing",
    "language",
    "natural language",
    "text analytics",
    "deep learning",
    "anomaly detection",
    "topic analysis",
    "tabular data"
]
__url__ = "https://www.kolibri-ml.com/"

# Maintainer, contributors, etc.
__maintainer__ = "Mohamed Ben Haddou"
__maintainer_email__ = "mbenhaddou@mentis.io"
__author__ = __maintainer__
__author_email__ = __maintainer_email__

# "Trove" classifiers for Python Package Index.
__classifiers__ = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: Education",
    "Intended Audience :: Information Technology",
    "Intended Audience :: Science/Research",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Topic :: Scientific/Engineering",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Scientific/Engineering :: Human Machine Interfaces",
    "Topic :: Scientific/Engineering :: Information Analysis",

]

from kolibri import default_configs

from kolibri.tokenizers import tokenize, tokenize_sentences
# support numpy from pypy

try:
    import numpypy
except ImportError:
    pass

import subprocess

if not hasattr(subprocess, "PIPE"):

    def _fake_PIPE(*args, **kwargs):
        raise NotImplementedError("subprocess.PIPE is not supported.")

    subprocess.PIPE = _fake_PIPE
if not hasattr(subprocess, "Popen"):

    def _fake_Popen(*args, **kwargs):
        raise NotImplementedError("subprocess.Popen is not supported.")

    subprocess.Popen = _fake_Popen

###########################################################
# TOP-LEVEL MODULES
###########################################################

# Import top-level functionality into top-level namespace


# Optional loading

try:
    import numpy
except ImportError:
    pass



from kolibri.data.downloader import download, download_shell
from kolibri.config import ModelConfig
from kolibri.model_loader import ModelLoader
from kolibri.model_trainer import ModelTrainer
from kolibri.backend import *
try:
    from kolibri.backend.tensorflow import tasks
except:
    pass


####################
#All exposed modules
####################

__all__ = [
    "data",
]

