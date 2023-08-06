from overrides import overrides

from kolibri.datasets.reader.base_reader import DatasetReader
import pandas as pd
from kolibri.tokenizers import WordTokenizer
from kolibri.data import find
import os, json
from logging import getLogger
from typing import Dict
log = getLogger(__name__)


class SnipsIntentCorpus(DatasetReader):
    """
    SNIPS dataset_train class

    Args:
            path (str): dataset_train path
            sentence_length (int, optional): max sentence length
            word_length (int, optional): max word length
    """

    __corpus_name__ = 'snips_intents'

    train_files = [
        "AddToPlaylist/train_AddToPlaylist_full.json",
        "BookRestaurant/train_BookRestaurant_full.json",
        "GetWeather/train_GetWeather_full.json",
        "PlayMusic/train_PlayMusic_full.json",
        "RateBook/train_RateBook_full.json",
        "SearchCreativeWork/train_SearchCreativeWork_full.json",
        "SearchScreeningEvent/train_SearchScreeningEvent_full.json",
    ]
    test_files = [
        "AddToPlaylist/validate_AddToPlaylist.json",
        "BookRestaurant/validate_BookRestaurant.json",
        "GetWeather/validate_GetWeather.json",
        "PlayMusic/validate_PlayMusic.json",
        "RateBook/validate_RateBook.json",
        "SearchCreativeWork/validate_SearchCreativeWork.json",
        "SearchScreeningEvent/validate_SearchScreeningEvent.json",
    ]


    def _load_dataset(self, dataset):
        """returns a tuple of train/test with 3-tuple of tokens, tags, intent_type"""
        if dataset == 'train':
            _data = self._load_intents(self.train_files)
        else:
            _data = self._load_intents(self.test_files)

        data = [(t, l, i) for i in sorted(_data) for t, l in _data[i]]

        return data

    def _load_intents(self, files):
        data = {}
        for f in sorted(files):
            fname = os.path.join(self.dataset_root, f)
            intent = f.split(os.sep)[0]
            with open(fname, encoding="utf-8", errors="ignore") as fp:
                fdata = json.load(fp)
            entries = self._parse_json([d["data"] for d in fdata[intent]])
            data[intent] = entries
        return data

    def _parse_json(self, data):
        tokenizer = WordTokenizer()
        sentences = []
        for s in data:
            tokens = []
            tags = []
            for t in s:
                new_tokens = tokenizer.tokenize(t["text"].strip())
                tokens += new_tokens
                ent = t.get("entity", None)
                if ent is not None:
                    tags += self._create_tags(ent, len(new_tokens))
                else:
                    tags += ["O"] * len(new_tokens)
            sentences.append((tokens, tags))
        return sentences

    @staticmethod
    def _create_tags(tag, length):
        labels = ["B-" + tag]
        if length > 1:
            for _ in range(length - 1):
                labels.append("I-" + tag)
        return labels

    def read(self, separator: str = None, task_name= "ner", *args, **kwargs):

        self.dataset_root =find('datasets/snips_intents')
        dataset_types=['train', 'test']
        data = {"train": [],
                "valid": [],
                "test": []}
        for dataset_type in dataset_types:
            file_name = kwargs.get(dataset_type, '{}.{}'.format(dataset_type, format))
            if file_name is None:
                continue

            data_set_raw = self._load_dataset(dataset_type)
            df = pd.DataFrame(data_set_raw, columns=['Content', 'Entities', 'Intent'])

            x = kwargs.get("x", "Content")
            if task_name in ["ner", "NER"]:
                y = kwargs.get('y', 'Entities')
            elif task_name in ["intent", "intents", "Intent", "Intents"]:
                y = kwargs.get('y', 'Intent')
            if isinstance(x, list):
                if separator is None:
                    # each sample is a tuple ("text", "label")
                    data[dataset_type] = [([row[x_] for x_ in x], str(row[y]))
                                              for _, row in df.iterrows()]
                else:
                    # each sample is a tuple ("text", ["label", "label", ...])
                    data[dataset_type] = [([row[x_] for x_ in x], row[y].split(separator))
                                              for _, row in df.iterrows()]
            else:
                if separator is None:
                    # each sample is a tuple ("text", "label")
                    data[dataset_type] = [(row[x], row[y]) for _, row in df.iterrows()]
                else:
                    # each sample is a tuple ("text", ["label", "label", ...])
                    data[dataset_type] = [(row[x], row[y].split(separator)) for _, row in df.iterrows()]

        self.data=data
        return self


#snips=SnipsIntentCorpus().read( task_name= "intent")