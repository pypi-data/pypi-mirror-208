

from typing import List, Union

from kolibri.core.component import Component

StrTokenReverserInfo = Union[List[str], List['StrTokenReverserInfo']]

class StrTokenReverser(Component):
    """Component for converting strings to strings with reversed token positions

    Args:
        tokenized: The parameter is only needed to reverse tokenized strings.
    """

    def __init__(self, tokenized: bool = False, *args, **kwargs) -> None:
        super().__init__()
        self.tokenized = tokenized

    @staticmethod
    def _reverse_str(raw_string):
        splitted = raw_string.split()
        splitted.reverse()
        string = ' '.join(splitted)
        return string

    @staticmethod
    def _reverse_tokens(raw_tokens):
        raw_tokens.reverse()
        return raw_tokens

    def transform(self, batch):
        """Recursively search for strings in a list and convert them to strings with reversed token positions

        Args:
            batch: a string or a list containing strings

        Returns:
            the same structure where all strings tokens are reversed
        """
        if isinstance(batch, (list, tuple)):
            batch = batch.copy()

        if self.tokenized:
            if isinstance(batch, (list, tuple)):
                if isinstance(batch[-1], str):
                    return self._reverse_tokens(batch)
                else:
                    return [self(line) for line in batch]
            raise RuntimeError(f'The objects passed to the reverser are not list or tuple! '
                               f' But they are {type(batch)}.'
                               f' If you want to passed str type directly use option tokenized = False')
        else:
            if isinstance(batch, (list, tuple)):
                return [self(line) for line in batch]
            else:
                return self._reverse_str(batch)
