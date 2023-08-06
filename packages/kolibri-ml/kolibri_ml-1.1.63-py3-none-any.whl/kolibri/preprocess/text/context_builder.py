from kolibri.core.component import Component
from kolibri.preprocess.text.cleaning.cleaning_scripts import fix_formating
from kdmt.dict import update
from kdmt.text import clean_text
from kolibri.preprocess.text.cleaning.email2text import EmailMessage

class LineContextBuilder(Component):

    provides = ["text"]
    defaults = {
        "fixed": {
            "context-size": 1
        },

        "tunable": {
        }
    }

    def __init__(self, config={}):
        super().__init__(config)
        self.override_default_parameters(config)
    def transform(self, X):
        return [self._build_context(x) for x in X]

    def _build_context(self, X):
        XX = []

        for l_idx in range(len(X)):
            context_line = []
            context_size=self.get_parameter("context-size", 1)
            for c in range(context_size):
                context_line.append("" if l_idx <c else X[l_idx - (context_size-c)])

            context_line.append(X[l_idx])

            for c in range(self.get_parameter("context-size", 1)):
                context_line.append("" if l_idx + (c+1) > len(X) - 1 else X[l_idx + (c + 1)])

            XX.append(context_line)
        return XX

    def fit(self, X, y):
        return self

    def update_default_hyper_parameters(self):
        self.defaults=update(self.defaults, LineContextBuilder.defaults)
        super().update_default_hyper_parameters()

