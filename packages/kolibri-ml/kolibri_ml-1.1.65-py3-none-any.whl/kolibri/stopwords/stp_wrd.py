import os
from kolibri.logger import get_logger

from kolibri.data import load
logger = get_logger(__name__)

STOP_WORDS_CACHE = {}



class Stopwords():

    def __init__(self):
        """
        :param with_additional_file: Allows to load LEFFF without the additional file. (Default: True)
        :type with_additional_file: bool
        :param load_only_pos: Allows to load LEFFF with only some pos tags: WordNet pos tags [a, r, n, v]. (Default: all)
        :type load_only_pos: list
        """
        #        data_file_path = os.path.dirname(os.path.realpath(__file__))
        from kolibri.data import load, find
        self.LANGUAGE_MAPPING=load("packages/stop-words/languages.json")
        if self.LANGUAGE_MAPPING is not None:
            self.AVAILABLE_LANGUAGES = list(self.LANGUAGE_MAPPING.values())
            self.stopwords_path=find("packages/stop-words")

class StopWordError(Exception):
    pass


__sw = Stopwords()


def get_stop_words(language, cache=True, aggressive=False):
    """
    :type language: basestring
    :rtype: list
    """
    try:
        language = __sw.LANGUAGE_MAPPING[language]
    except KeyError:
        if language not in __sw.AVAILABLE_LANGUAGES:
            raise StopWordError('{0}" language is unavailable.'.format(
                language
            ))

    if cache and language in STOP_WORDS_CACHE:
        return STOP_WORDS_CACHE[language]
    language_name = language
    if aggressive:
        language_name + "-aggressive"



    try:
        language_filename = os.path.join(__sw.stopwords_path, language_name + '.txt')
        stop_words=load("packages/stop-words/"+language_name + '.txt', as_array=True)
    except IOError:
        raise StopWordError(
            '{0}" file is unreadable, check your installation.'.format(
                language_filename
            )
        )

    if cache:
        STOP_WORDS_CACHE[language] = stop_words

    return stop_words


if __name__ == "__main__":
    stp = get_stop_words('en')

    print(stp)
