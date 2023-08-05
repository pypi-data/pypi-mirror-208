from kolibri.features.basefeaturizer import BaseFeaturizer
from kolibri.logger import get_logger
import numpy as np
import inspect
import kolibri.features.text.feature_functions as ffunctions

logger = get_logger(__name__)



class TextFeatureExtractor(BaseFeaturizer):

    provides = ["text_features"]

    requires = []

    defaults = {
            "fixed": {

                # regular expression for tokens
                "token-pattern": r'(?u)\b\w\w+\b',

                # remove accents during the preprocessing step
                "strip-accents": None,  # {'ascii', 'unicode', None}

                "min-ngram": 1,  # int

                "context-size":1
            },

            "tunable": {
                "return_count": {
                    "description": "",
                    "value": False,
                    "type": "boolean"
                },
                "has_email": {
                    "description": "",
                    "value": True,
                    "type": "boolean"
                },
                "has_only_quotes": {
                    "description": "",
                    "value": True,
                    "type": "boolean"
                },
                "contains_phone": {
                    "description": "",
                    "value": True,
                    "type": "boolean"
                },
                "count_named_entities": {
                    "description": "",
                    "value": True,
                    "type": "boolean"
                },
                "is_in_last_n_lines": {
                    "description": "",
                    "value": True,
                    "type": "boolean"
                },
                "is_in_second_half": {
                    "description": "",
                    "value": True,
                    "type": "boolean"
                },
                "contains_word_from_list": {
                    "description": "",
                    "value": True,
                    "type": "boolean"
                },
                "has_url": {
                    "description": "",
                    "value": True,
                    "type": "boolean"
                },
                "number_count": {
                    "description": "",
                    "value": True,
                    "type": "boolean"
                },
                "word_count": {
                    "description": "",
                    "value": True,
                    "type": "boolean"
                },
                "char_count": {
                    "description": "",
                    "value": True,
                    "type": "boolean"
                },
                "avg_word_length": {
                    "description": "",
                    "value": True,
                    "type": "boolean"
                },
                "hashtags_count": {
                    "description": "",
                    "value": True,
                    "type": "boolean"
                },
                "user_mentions_count": {
                    "description": "",
                    "value": True,
                    "type": "boolean"
                },
                "links_count": {
                    "description": "",
                    "value": True,
                    "type": "boolean"
                },
                "count_punc": {
                    "description": "",
                    "value": True,
                    "type": "boolean"
                },
                "perc_cap_words": {
                    "description": "",
                    "value": True,
                    "type": "boolean"
                },
            }
        }

    @classmethod
    def required_packages(cls):
        return ["sklearn"]

    def line_to_vec(self, l, t):
        curr_res = list()
        curr_res.append(txt_prep.contains_phone(l))
        curr_res.append(txt_prep.contains_signature_word(l))
        curr_res.append(txt_prep.has_only_quotes(l))
        curr_res.append(txt_prep.contains_email(l))
        curr_res.append(txt_prep.has_url(l))
#        curr_res.append(txt_prep.count_named_entities(l))
        curr_res.append(txt_prep.is_under_closing_phrase(t, l))
        curr_res.append(txt_prep.is_in_second_part(t, l))
        curr_res.append(txt_prep.is_in_last_five_lines(t, l))

        curr_res = [int(elem) for elem in curr_res]
        return curr_res

    def _to_vect(self, x, X):
        results=[]
        for func in self.hyperparameters["tunable"]:
            if func in dir(ffunctions):
                funct= getattr(ffunctions, func)
                if inspect.isfunction(funct):
                    try:
                        results.append(funct(x, X))
                    except Exception as e:
                        print(e)



    def transform(self, X, **kwargs):
        result = []

        for text in X:
            for line in text:
                curr_res=[]
                for c in range(self.get_parameter("context-size")):
                    curr_res.extend(self._to_vect(line[c], text))
                    result.append(curr_res)
        return np.array(result)

    def transform_(self, X, **kwargs):
        result = []

        for (t, l, prevLine, nextLine) in X:
            curr_line_vec = self.line_to_vec(l, t)
            prev_line_vec = self.line_to_vec(prevLine, t)
            next_line_vec = self.line_to_vec(nextLine, t)
            curr_res = next_line_vec + prev_line_vec + curr_line_vec
            result.append(curr_res)
        return np.array(result)

    def fit(self, X, y=None, **kwargs):
        return self

    def get_params(self, **kwargs):
        return {}