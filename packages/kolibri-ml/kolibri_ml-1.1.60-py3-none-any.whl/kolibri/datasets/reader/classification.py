
from logging import getLogger
from pathlib import Path

import pandas as pd
from overrides import overrides

from kolibri.datasets.reader.base_reader import DatasetReader
from kdmt.download import download
log = getLogger(__name__)


class ClassificationDatasetReader(DatasetReader):
    """
    Class provides reading dataset in .csv format
    """

    @overrides
    def read(self, data_path: str, url: str = None,
             format: str = "csv", separator: str = None,
             *args, **kwargs) -> dict:
        """
        Read dataset from data_path directory. or from an url

        Args:
            data_path: directory with files
            url: download data files if data_path not exists or empty
            format: extension of files. Set of Values: ``"csv", "json"``
            separator: string separator of labels in column with labels
            sep (str): delimeter for ``"csv"`` files. Default: None -> only one class per sample
            header (int): row number to use as the column names
            names (array): list of column names to use
            orient (str): indication of expected JSON string format
            lines (boolean): read the file as a json object per line. Default: ``False``

        Returns:
            dictionary with types from dataset_types.
            Each field of dictionary is a list of tuples (x_i, y_i)
        """
        dataset_types = ["train", "valid", "test"]

        train_file = kwargs.get('train', 'train.csv')

        if not Path(data_path, train_file).exists():
            if url is None:
                raise Exception(
                    "data path {} does not exist or is empty, and download url parameter not specified!".format(
                        data_path))
            log.info("Loading train data from {} to {}".format(url, data_path))
            download(url=url, destination_name=Path(data_path, train_file))

        data = {"train": [],
                "valid": [],
                "test": []}
        for dataset_type in dataset_types:
            file_name = kwargs.get(dataset_type, '{}.{}'.format(dataset_type, format))
            if file_name is None:
                continue
            
            file = Path(data_path).joinpath(file_name)
            if file.exists():
                if format == 'csv':
                    keys = ('sep', 'header', 'names')
                    options = {k: kwargs[k] for k in keys if k in kwargs}
                    df = pd.read_csv(file, **options)
                elif format == 'json':
                    keys = ('orient', 'lines')
                    options = {k: kwargs[k] for k in keys if k in kwargs}
                    df = pd.read_json(file, **options)
                else:
                    raise Exception('Unsupported file format: {}'.format(format))

                x = kwargs.get("x", "text")
                y = kwargs.get('y', 'labels')
                if isinstance(x, list):
                    if separator is None:
                        # each sample is a tuple ("text", "label")
                        data[dataset_type] = [([row[x_] for x_ in x], str(row[y]))
                                           for _, row in df.iterrows()]
                    else:
                        # each sample is a tuple ("text", ["label", "label", ...])
                        data[dataset_type] = [([row[x_] for x_ in x], str(row[y]).split(separator))
                                           for _, row in df.iterrows()]
                else:
                    if separator is None:
                        # each sample is a tuple ("text", "label")
                        data[dataset_type] = [(row[x], str(row[y])) for _, row in df.iterrows()]
                    else:
                        # each sample is a tuple ("text", ["label", "label", ...])
                        data[dataset_type] = [(row[x], str(row[y]).split(separator)) for _, row in df.iterrows()]
            else:
                log.warning("Cannot find {} file".format(file))

        return data
