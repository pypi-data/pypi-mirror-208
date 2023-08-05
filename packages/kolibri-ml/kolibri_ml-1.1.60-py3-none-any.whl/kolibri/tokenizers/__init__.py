from kolibri.tokenizers.kolibri_tokenizer import KolibriTokenizer
from kolibri.tokenizers.char_tokenizer import CharTokenizer
from kolibri.tokenizers.regex_tokenizer import RegexpTokenizer
from kolibri.tokenizers.word_tokenizer import WordTokenizer
from kolibri.tokenizers.sentence_tokenizer import SentenceTokenizer
from kolibri.tokenizers.ugc_tokenizer import UGCTokenizer
from kolibri.tokenizers.bert_tokenizer import BertTokenizer

# Standard sentence tokenizer.
def tokenize_sentences(text):
    """
    Return a sentence-tokenized copy of *text*,
    using NLTK's recommended sentence tokenizer
    (currently :class:`.PunktSentenceTokenizer`
    for the specified language).

    :param text: text to split into sentences
    :param language: the model name in the Punkt corpus
    """
    tokenizer = SentenceTokenizer()
    return tokenizer.tokenize(text)


# Standard word tokenizer.
_word_tokenizer = WordTokenizer()


def tokenize(text, language="english"):
    """
    Return a tokenized copy of *text*,
    for the specified language).

    :param text: text to split into words
    :type text: str
    :param language: the model name in the Punkt corpus
    :type language: str
    :param preserve_line: A flag to decide whether to sentence tokenize the text or not.
    :type preserve_line: bool
    """

#    if language not in ["english", "en"]:
#        _word_tokenizer=WordTokenizer({"language": language})

    return _word_tokenizer.tokenize(text)
