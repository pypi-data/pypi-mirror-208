# encoding: utf-8



# file: types.py
# time: 3:54 

from typing import List, Union, Tuple

TextSamplesVar = List[List[str]]
NumSamplesListVar = List[List[int]]
LabelSamplesVar = Union[TextSamplesVar, List[str]]

ClassificationLabelVar = List[str]
MultiLabelClassificationLabelVar = Union[List[List[str]], List[Tuple[str]]]

if __name__ == "__main__":
    pass
