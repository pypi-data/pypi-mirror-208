#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'mohamedbenhaddou'

from kolibri.tokenizers.tokenizer import Tokenizer
from kolibri.stopwords import get_stop_words
from kdmt.dict import update
import numpy as np
import os, joblib
from kolibri.logger import get_logger
from kolibri.data import load

from kolibri.tools._regex import Regex
from kolibri.tools.scanner import Scanner

logger=get_logger(__name__)
import string


class Token(object):
    def __init__(self, text, start=-1, index=-1, data=None, lemma=None, pos=None, entity=None):
        self.index=index
        self.start = start
        self.text = text
        self.end = start + len(text)
        self.abstract=None
        self.data = data if data else {}
        self.lemma=lemma
        self.pos=pos
        self.tag=None
        self.entity=entity
        self.is_stopword=False
        self.patterns={}

    def set(self, prop, info):
        self.data[prop] = info

    def get(self, prop, default=None):
        return self.data.get(prop, default)

    def tojson(self):
        return {"index": self.index, "text": self.text, "lemma": self.lemma, "pos": self.pos, "entity": self.entity}


class Tokens(list):

    def addToken(self, token):
        list.append(token)


    def get_tokens_as_strings(self, removePunctuations=True):
        if removePunctuations:
            return [t.value for t in self if t.value not in string.punctuation]
        return [t.value for t in self if t.value]


class KolibriTokenizer(Tokenizer):
    provides = ["tokens"]

    defaults = {
        "fixed": {
            "outout-type": "strings" #"tokens"
        },
        "tunable": {
            "abstract-entities": {
                "value": True,
                "type": "categorical",
                "values": [True, False]
            },
            "group-entities": {
                "value": False,
                "type": "categorical",
                "values": [True, False]
            }

        }
    }

    def __init__(self, configs=None):
        super().__init__(configs)
        from kolibri.tools import regexes as common_regs
        regexes = load('packages/tokenizers/default_regexes.json')

        for (name, regex_variable) in regexes.items():
            setattr(self, name, Regex(regex_variable["label"], regex_variable["value"], regex_variable["flags"] if "flags" in regex_variable else 0) )



        self.stopwords = None
        if "language" in self.hyperparameters["fixed"]["language"]:
            self.language = self.hyperparameters["fixed"]["language"]
            self.stopwords = get_stop_words(self.language)


        lang=self.language.upper()


        self.patterns =[self.EXCEPTIONS, common_regs.URL, common_regs.MONEY]
        if lang in common_regs.DATE:
            self.patterns.append(common_regs.DATE[lang])

        self.patterns.append(common_regs.TIME)
        if lang in common_regs.MONTH:
            self.patterns.append(common_regs.MONTH[lang])

        self.patterns.append(common_regs.DURATION)

        for phone in list(common_regs.PHONE_NUMBER.values()):
            self.patterns.append(phone)

        self.patterns.extend([self.OPENPARENTHESIS, self.CLOSEPARENTHESIS, self.IBAN,  self.WS,self.URL, self.ENERGY_INDEX, self.EMAIL, self.MULTIPLEWORD,  self.ACORNYM,self.NUM, self.PLUS, self.MINUS, self.ELLIPSIS, self.DOT, self.TIMES, self.EQ,
                 self.QUESTION, self.CLIENT_NR,
                 self.EXLAMATION, self.COLON, self.COMA, self.SEMICOLON, self.OPENQOTE, self.ENDQOTE, self.DOUBLEQOTE, self.SINGLEQOTE, self.PIPE])

        self.patterns.extend([self.CANDIDATE,  self.WORD, self.OTHER])
        self.scanner=Scanner(self.patterns)


    def tokenize(self, text):

        text = str(text).replace(r'\u2019', '\'')
#        tokens=self.scanner.scan(text)
        tokens=self.generate_tokens(text)

        tokens= [token for token in tokens if token.get('type') not in ['WS']]

        if self.get_parameter('outout-type') in ["tokens", "token"]:
            return tokens

        elif self.get_parameter("abstract-entities"):
            tokens=['__'+t.get('type')+'__' if t.get('type') in ['WA', 'URL', 'EMAIL', 'CLIENT_NR','IBAN', 'EAN', 'MONEY', 'DATE', 'MONTH', 'DURATION', 'NUMBER', 'ENERGY_INDEX', 'PHONE_NUMBER','FILE'] else t.text for t in tokens]
        else:
            tokens=[t.text  for t in tokens]

        return tokens

    def generate_tokens(self, text):
        text = text.replace(r'\u2019', '\'')
        scanned = self.scanner.scan(text)
        i = 0
        for m in iter(scanned):
            t = Token(text=m['text'], start=m['pos'], index=i)
            t.set('type', m['label'])
            i += 1
            yield t

    @classmethod
    def load(cls,
             model_dir=None, model_metadata=None, cached_component=None, **kwargs):

        if model_metadata is not None:
            if model_metadata.get("folder") is not None:
                model_dir = model_metadata.get("folder")
            if model_dir and model_metadata.get("model_file"):
                file_name = model_metadata.get("model_file")
                model_file = os.path.join(model_dir, file_name)
                tokenizer= joblib.load(model_file)
                tokenizer.scanner = Scanner(tokenizer.patterns)
                return tokenizer

            else:
                logger.warning("Failed to load component. Maybe path {} "
                               "doesn't exist".format(os.path.abspath(model_dir)))
                tokenizer= cls(model_metadata)
                tokenizer.scanner=Scanner(tokenizer.patterns)
                return tokenizer
        else:
            model_file = os.path.join(model_dir, cls.name + ".pkl")
            tokenizer = joblib.load(model_file)
            tokenizer.scanner = Scanner(tokenizer.patterns)
            return tokenizer

    def transform(self, X):
        X=self._check_values(X)
        if not isinstance(X, list) and not isinstance(X, np.ndarray):
            X=[X]
        tokenized=[]
        for i, x in enumerate(X):
            tokenized.append(self.tokenize(x))
#        tokenized= [self.tokenize(x) for x in X]
        return tokenized


    def update_default_hyper_parameters(self):
        self.defaults=update(self.defaults, KolibriTokenizer.defaults)
        super().update_default_hyper_parameters()


    def __getstate__(self):
        """Return state values to be pickled."""
        return (self.hyperparameters, self.patterns)

    def __setstate__(self, state):
        """Restore state from the unpickled state values."""
        self.hyperparameters, self.patterns = state



if __name__=='__main__':
    tokenizer = KolibriTokenizer({"abstract-entities":True})
    text = """De rekening van Darren Mertens, klant 281972 te Begonialaan 32/1, 1853 Grimbergen kan worden afgesloten. De flat is verkocht.
Bijgevoegd vindt u het energieovername document. Gaz: 23344,3 m3
Indien u nog vragen heeft, mag u die stellen via mail of telefoon 0472 310 709 VAN Darren Mertens.

"""
    tokens = tokenizer.tokenize(text)

    [print(t) for t in tokens]