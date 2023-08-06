from logging import getLogger

from kolibri.core.component import Component

log = getLogger(__name__)


class CharSplitter(Component):
    """This component transforms batch of sequences of tokens into batch of sequences of character sequences."""

    def __init__(self, **kwargs):
        super().__init__()


    def transform(self, X):
        char_batch = []
        for tokens_sequence in X:
            char_batch.append([list(tok) for tok in tokens_sequence])
        return char_batch


if __name__=="__main__":
    charsplit=CharSplitter()
    print(charsplit.transform('Hello world'))