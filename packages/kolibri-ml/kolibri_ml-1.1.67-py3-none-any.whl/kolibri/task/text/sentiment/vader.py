import math
import re
import string
from itertools import product
from itertools import tee
from kolibri.data import load
import numpy as np
import pandas as pd


def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


class Lexicon:

    def __init__(self, dataframe, tag_names, source, language='english'):
        self.dataframe = dataframe
        self.dataframe.rename(columns={c: Lexicon.reformat_language_name(c) for c in self.dataframe.columns},
                              inplace=True)
        self.tag_names = tag_names
        self.source = source
        self.language = language
        tags = np.asarray(self.dataframe[self.tag_names])
        self.table = {}
        for language in self.dataframe.columns:
            if language in tag_names:
                continue
            if language.startswith('unnamed'):
                continue

            words = self.dataframe[language]
            if isinstance(words, pd.DataFrame):
                words = words.iloc[:, 0]

            for key, value in zip(words, tags):
                if key not in self.table:
                    self.table[key] = {}
                self.table[key][language] = value

    @staticmethod
    def reformat_language_name(name):
        name = name.lower().strip()
        if '(' in name:
            name = name.split('(')[0].strip()
        return name

    def get(self, token):
        return self.table.get(token, None)

    def get_n_tags(self):
        return len(self.tag_names)

    def get_tag_names(self):
        return self.tag_names

    def process(self, tokens, as_dict=True):

        n_tags = self.get_n_tags()
        language_counts = {}
        counts = {}
        for token in tokens:
            results = self.get(token.lower())
            if results is not None:
                for language in results.keys():
                    if language not in counts:
                        counts[language] = np.zeros(n_tags, dtype=np.int)
                    counts[language] += results[language]
                    if language not in language_counts:
                        language_counts[language] = 0
                    language_counts[language] += 1

        if len(counts) == 0:
            counters = np.zeros(n_tags, dtype=np.int)
        else:
            # Select language
            if self.language == 'auto':
                languages = list(language_counts.keys())
                total_counts = [language_counts[language] for language in languages]
                language = languages[np.argmax(total_counts)]
                counters = counts[language]
            else:
                language = self.language
            if language not in counts:
                # raise LexiconException(f'Could not find language "{language}". Found: {counts.keys()}')
                counters = np.zeros(n_tags, dtype=np.int)
            else:
                counters = counts[language]

        if as_dict:
            data = {name: counter for name, counter in zip(self.tag_names, counters)}
            data['lang'] = language
            return data
        else:
            return counters

    def __len__(self):
        return len(self.dataframe)


class LexiconConstants:
    """
    A class to keep the Lexicons lists and constants.
    """
    ##Constants##
    # (empirically derived mean sentiment intensity rating increase for booster words)
    B_INCR = 0.293
    B_DECR = -0.293
    N_SCALAR = -0.74
    # (empirically derived mean sentiment intensity rating increase for using
    # ALLCAPs to emphasize a word)
    C_INCR = 0.733
    # for removing punctuation
    REGEX_REMOVE_PUNCTUATION = re.compile(f"[{re.escape(string.punctuation)}]")

    PUNC_LIST = [
        ".",
        "!",
        "?",
        ",",
        ";",
        ":",
        "-",
        "'",
        '"',
        "!!",
        "!!!",
        "??",
        "???",
        "?!?",
        "!?!",
        "?!?!",
        "!?!?",
    ]

    def __init__(self, langauge='en'):
        self.NEGATE = load(f"packages/gazetteers/{langauge}/negation.txt", format="set")

        # booster/dampener 'intensifiers' or 'degree adverbs'
        # https://en.wiktionary.org/wiki/Category:English_degree_adverbs

        self.BOOSTER_DICT = {
            "absolutely": self.B_INCR,
            "amazingly": self.B_INCR,
            "awfully": self.B_INCR,
            "completely": self.B_INCR,
            "considerably": self.B_INCR,
            "decidedly": self.B_INCR,
            "deeply": self.B_INCR,
            "effing": self.B_INCR,
            "enormously": self.B_INCR,
            "entirely": self.B_INCR,
            "especially": self.B_INCR,
            "exceptionally": self.B_INCR,
            "extremely": self.B_INCR,
            "fabulously": self.B_INCR,
            "flipping": self.B_INCR,
            "flippin": self.B_INCR,
            "fricking": self.B_INCR,
            "frickin": self.B_INCR,
            "frigging": self.B_INCR,
            "friggin": self.B_INCR,
            "fully": self.B_INCR,
            "fucking": self.B_INCR,
            "greatly": self.B_INCR,
            "hella": self.B_INCR,
            "highly": self.B_INCR,
            "hugely": self.B_INCR,
            "incredibly": self.B_INCR,
            "intensely": self.B_INCR,
            "majorly": self.B_INCR,
            "more": self.B_INCR,
            "most": self.B_INCR,
            "particularly": self.B_INCR,
            "purely": self.B_INCR,
            "quite": self.B_INCR,
            "really": self.B_INCR,
            "remarkably": self.B_INCR,
            "so": self.B_INCR,
            "substantially": self.B_INCR,
            "thoroughly": self.B_INCR,
            "totally": self.B_INCR,
            "tremendously": self.B_INCR,
            "uber": self.B_INCR,
            "unbelievably": self.B_INCR,
            "unusually": self.B_INCR,
            "utterly": self.B_INCR,
            "very": self.B_INCR,
            "almost": self.B_DECR,
            "barely": self.B_DECR,
            "hardly": self.B_DECR,
            "just enough": self.B_DECR,
            "kind of": self.B_DECR,
            "kinda": self.B_DECR,
            "kindof": self.B_DECR,
            "kind-of": self.B_DECR,
            "less": self.B_DECR,
            "little": self.B_DECR,
            "marginally": self.B_DECR,
            "occasionally": self.B_DECR,
            "partly": self.B_DECR,
            "scarcely": self.B_DECR,
            "slightly": self.B_DECR,
            "somewhat": self.B_DECR,
            "sort of": self.B_DECR,
            "sorta": self.B_DECR,
            "sortof": self.B_DECR,
            "sort-of": self.B_DECR,
        }

        # check for special case idioms using a sentiment-laden keyword known to SAGE
        self.SPECIAL_CASE_IDIOMS = {
            "the shit": 3,
            "the bomb": 3,
            "bad ass": 1.5,
            "yeah right": -2,
            "cut the mustard": 2,
            "kiss of death": -1.5,
            "hand to mouth": -2,
        }

    def negated(self, input_words, include_nt=True):
        """
        Determine if input contains negation words
        """
        neg_words = self.NEGATE
        if any(word.lower() in neg_words for word in input_words):
            return True
        if include_nt:
            if any("n't" in word.lower() for word in input_words):
                return True
        for first, second in pairwise(input_words):
            if second.lower() == "least" and first.lower() != "at":
                return True
        return False

    def normalize(self, score, alpha=15):
        """
        Normalize the score to be between -1 and 1 using an alpha that
        approximates the max expected value
        """
        norm_score = score / math.sqrt((score * score) + alpha)
        return norm_score

    def scalar_inc_dec(self, word, valence, is_cap_diff):
        """
        Check if the preceding words increase, decrease, or negate/nullify the
        valence
        """
        scalar = 0.0
        word_lower = word.lower()
        if word_lower in self.BOOSTER_DICT:
            scalar = self.BOOSTER_DICT[word_lower]
            if valence < 0:
                scalar *= -1
            # check if booster/dampener word is in ALLCAPS (while others aren't)
            if word.isupper() and is_cap_diff:
                if valence > 0:
                    scalar += self.C_INCR
                else:
                    scalar -= self.C_INCR
        return scalar


class SentiText:
    """
    Identify sentiment-relevant string-level properties of input text.
    """

    def __init__(self, text, punc_list, regex_remove_punctuation):
        if not isinstance(text, str):
            text = str(text.encode("utf-8"))
        self.text = text
        self.PUNC_LIST = punc_list
        self.REGEX_REMOVE_PUNCTUATION = regex_remove_punctuation
        self.words_and_emoticons = self._words_and_emoticons()
        # doesn't separate words from
        # adjacent punctuation (keeps emoticons & contractions)
        self.is_cap_diff = self.allcap_differential(self.words_and_emoticons)

    def _words_plus_punc(self):
        """
        Returns mapping of form:
        {
            'cat,': 'cat',
            ',cat': 'cat',
        }
        """
        no_punc_text = self.REGEX_REMOVE_PUNCTUATION.sub("", self.text)
        # removes punctuation (but loses emoticons & contractions)
        words_only = no_punc_text.split()
        # remove singletons
        words_only = {w for w in words_only if len(w) > 1}
        # the product gives ('cat', ',') and (',', 'cat')
        punc_before = {"".join(p): p[1] for p in product(self.PUNC_LIST, words_only)}
        punc_after = {"".join(p): p[0] for p in product(words_only, self.PUNC_LIST)}
        words_punc_dict = punc_before
        words_punc_dict.update(punc_after)
        return words_punc_dict

    def _words_and_emoticons(self):
        """
        Removes leading and trailing puncutation
        Leaves contractions and most emoticons
            Does not preserve punc-plus-letter emoticons (e.g. :D)
        """
        wes = self.text.split()
        words_punc_dict = self._words_plus_punc()
        wes = [we for we in wes if len(we) > 1]
        for i, we in enumerate(wes):
            if we in words_punc_dict:
                wes[i] = words_punc_dict[we]
        return wes

    def allcap_differential(self, words):
        """
        Check whether just some words in the input are ALL CAPS

        :param list words: The words to inspect
        :returns: `True` if some but not all items in `words` are ALL CAPS
        """
        is_different = False
        allcap_words = 0
        for word in words:
            if word.isupper():
                allcap_words += 1
        cap_differential = len(words) - allcap_words
        if 0 < cap_differential < len(words):
            is_different = True
        return is_different


class SentimentIntensityAnalyzer:
    """
    Give a sentiment intensity score to sentences.
    """

    def __init__(
            self,
            lexicon_file="packages/sentiment/lexicons/vader/vader_lexicon.txt",
    ):
        self.lexicon_file = load(lexicon_file)

        self.constants = LexiconConstants()
        self.lexicon = self.make_lex_dict()
    def make_lex_dict(self):
        """
        Convert lexicon file to a dictionary
        """
        lex_dict = {}
        for line in self.lexicon_file.split("\n"):
            (word, measure) = line.strip().split("\t")[0:2]
            lex_dict[word] = float(measure)
        return lex_dict

    def polarity_scores(self, text):
        """
        Return a float for sentiment strength based on the input text.
        Positive values are positive valence, negative value are negative
        valence.
        """
        # text, words_and_emoticons, is_cap_diff = self.preprocess(text)
        sentitext = SentiText(
            text, self.constants.PUNC_LIST, self.constants.REGEX_REMOVE_PUNCTUATION
        )
        sentiments = []
        words_and_emoticons = sentitext.words_and_emoticons
        for i, item in enumerate(words_and_emoticons):
            valence = 0
#            i = words_and_emoticons.index(item)
            if (
                    i < len(words_and_emoticons) - 1
                    and item.lower() == "kind"
                    and words_and_emoticons[i + 1].lower() == "of"
            ) or item.lower() in self.constants.BOOSTER_DICT:
                sentiments.append(valence)
                continue

            sentiments = self.sentiment_valence(valence, sentitext, item, i, sentiments)

        sentiments = self._but_check(words_and_emoticons, sentiments)

        return self.score_valence(sentiments, text)

    def sentiment_valence(self, valence, sentitext, item, i, sentiments):
        is_cap_diff = sentitext.is_cap_diff
        words_and_emoticons = sentitext.words_and_emoticons
        item_lowercase = item.lower()
        if item_lowercase in self.lexicon:
            # get the sentiment valence
            valence = self.lexicon[item_lowercase]

            # check if sentiment laden word is in ALL CAPS (while others aren't)
            if item.isupper() and is_cap_diff:
                if valence > 0:
                    valence += self.constants.C_INCR
                else:
                    valence -= self.constants.C_INCR

            for start_i in range(0, 3):
                if (
                        i > start_i
                        and words_and_emoticons[i - (start_i + 1)].lower()
                        not in self.lexicon
                ):
                    # dampen the scalar modifier of preceding words and emoticons
                    # (excluding the ones that immediately preceed the item) based
                    # on their distance from the current item.
                    s = self.constants.scalar_inc_dec(
                        words_and_emoticons[i - (start_i + 1)], valence, is_cap_diff
                    )
                    if start_i == 1 and s != 0:
                        s = s * 0.95
                    if start_i == 2 and s != 0:
                        s = s * 0.9
                    valence = valence + s
                    valence = self._never_check(
                        valence, words_and_emoticons, start_i, i
                    )
                    if start_i == 2:
                        valence = self._idioms_check(valence, words_and_emoticons, i)

                        # future work: consider other sentiment-laden idioms
                        # other_idioms =
                        # {"back handed": -2, "blow smoke": -2, "blowing smoke": -2,
                        #  "upper hand": 1, "break a leg": 2,
                        #  "cooking with gas": 2, "in the black": 2, "in the red": -2,
                        #  "on the ball": 2,"under the weather": -2}

            valence = self._least_check(valence, words_and_emoticons, i)

        sentiments.append(valence)
        return sentiments

    def _least_check(self, valence, words_and_emoticons, i):
        # check for negation case using "least"
        if (
                i > 1
                and words_and_emoticons[i - 1].lower() not in self.lexicon
                and words_and_emoticons[i - 1].lower() == "least"
        ):
            if (
                    words_and_emoticons[i - 2].lower() != "at"
                    and words_and_emoticons[i - 2].lower() != "very"
            ):
                valence = valence * self.constants.N_SCALAR
        elif (
                i > 0
                and words_and_emoticons[i - 1].lower() not in self.lexicon
                and words_and_emoticons[i - 1].lower() == "least"
        ):
            valence = valence * self.constants.N_SCALAR
        return valence

    def _but_check(self, words_and_emoticons, sentiments):
        words_and_emoticons = [w_e.lower() for w_e in words_and_emoticons]
        but = {"but"} & set(words_and_emoticons)
        if but:
            bi = words_and_emoticons.index(next(iter(but)))
            for sidx, sentiment in enumerate(sentiments):
                if sidx < bi:
                    sentiments[sidx] = sentiment * 0.5
                elif sidx > bi:
                    sentiments[sidx] = sentiment * 1.5
        return sentiments

    def _idioms_check(self, valence, words_and_emoticons, i):
        onezero = f"{words_and_emoticons[i - 1]} {words_and_emoticons[i]}"

        twoonezero = "{} {} {}".format(
            words_and_emoticons[i - 2],
            words_and_emoticons[i - 1],
            words_and_emoticons[i],
        )

        twoone = f"{words_and_emoticons[i - 2]} {words_and_emoticons[i - 1]}"

        threetwoone = "{} {} {}".format(
            words_and_emoticons[i - 3],
            words_and_emoticons[i - 2],
            words_and_emoticons[i - 1],
        )

        threetwo = "{} {}".format(
            words_and_emoticons[i - 3], words_and_emoticons[i - 2]
        )

        sequences = [onezero, twoonezero, twoone, threetwoone, threetwo]

        for seq in sequences:
            if seq in self.constants.SPECIAL_CASE_IDIOMS:
                valence = self.constants.SPECIAL_CASE_IDIOMS[seq]
                break

        if len(words_and_emoticons) - 1 > i:
            zeroone = f"{words_and_emoticons[i]} {words_and_emoticons[i + 1]}"
            if zeroone in self.constants.SPECIAL_CASE_IDIOMS:
                valence = self.constants.SPECIAL_CASE_IDIOMS[zeroone]
        if len(words_and_emoticons) - 1 > i + 1:
            zeroonetwo = "{} {} {}".format(
                words_and_emoticons[i],
                words_and_emoticons[i + 1],
                words_and_emoticons[i + 2],
            )
            if zeroonetwo in self.constants.SPECIAL_CASE_IDIOMS:
                valence = self.constants.SPECIAL_CASE_IDIOMS[zeroonetwo]

        # check for booster/dampener bi-grams such as 'sort of' or 'kind of'
        if (
                threetwo in self.constants.BOOSTER_DICT
                or twoone in self.constants.BOOSTER_DICT
        ):
            valence = valence + self.constants.self.B_DECR
        return valence

    def _never_check(self, valence, words_and_emoticons, start_i, i):
        if start_i == 0:
            if self.constants.negated([words_and_emoticons[i - 1]]):
                valence = valence * self.constants.N_SCALAR
        if start_i == 1:
            if words_and_emoticons[i - 2] == "never" and (
                    words_and_emoticons[i - 1] == "so"
                    or words_and_emoticons[i - 1] == "this"
            ):
                valence = valence * 1.5
            elif self.constants.negated([words_and_emoticons[i - (start_i + 1)]]):
                valence = valence * self.constants.N_SCALAR
        if start_i == 2:
            if (
                    words_and_emoticons[i - 3] == "never"
                    and (
                    words_and_emoticons[i - 2] == "so"
                    or words_and_emoticons[i - 2] == "this"
            )
                    or (
                    words_and_emoticons[i - 1] == "so"
                    or words_and_emoticons[i - 1] == "this"
            )
            ):
                valence = valence * 1.25
            elif self.constants.negated([words_and_emoticons[i - (start_i + 1)]]):
                valence = valence * self.constants.N_SCALAR
        return valence

    def _punctuation_emphasis(self, sum_s, text):
        # add emphasis from exclamation points and question marks
        ep_amplifier = self._amplify_ep(text)
        qm_amplifier = self._amplify_qm(text)
        punct_emph_amplifier = ep_amplifier + qm_amplifier
        return punct_emph_amplifier

    def _amplify_ep(self, text):
        # check for added emphasis resulting from exclamation points (up to 4 of them)
        ep_count = text.count("!")
        if ep_count > 4:
            ep_count = 4
        # (empirically derived mean sentiment intensity rating increase for
        # exclamation points)
        ep_amplifier = ep_count * 0.292
        return ep_amplifier

    def _amplify_qm(self, text):
        # check for added emphasis resulting from question marks (2 or 3+)
        qm_count = text.count("?")
        qm_amplifier = 0
        if qm_count > 1:
            if qm_count <= 3:
                # (empirically derived mean sentiment intensity rating increase for
                # question marks)
                qm_amplifier = qm_count * 0.18
            else:
                qm_amplifier = 0.96
        return qm_amplifier

    def _sift_sentiment_scores(self, sentiments):
        # want separate positive versus negative sentiment scores
        pos_sum = 0.0
        neg_sum = 0.0
        neu_count = 0
        for sentiment_score in sentiments:
            if sentiment_score > 0:
                pos_sum += (
                        float(sentiment_score) + 1
                )  # compensates for neutral words that are counted as 1
            if sentiment_score < 0:
                neg_sum += (
                        float(sentiment_score) - 1
                )  # when used with math.fabs(), compensates for neutrals
            if sentiment_score == 0:
                neu_count += 1
        return pos_sum, neg_sum, neu_count

    def score_valence(self, sentiments, text):
        if sentiments:
            sum_s = float(sum(sentiments))
            # compute and add emphasis from punctuation in text
            punct_emph_amplifier = self._punctuation_emphasis(sum_s, text)
            if sum_s > 0:
                sum_s += punct_emph_amplifier
            elif sum_s < 0:
                sum_s -= punct_emph_amplifier

            compound = self.constants.normalize(sum_s)
            # discriminate between positive, negative and neutral sentiment scores
            pos_sum, neg_sum, neu_count = self._sift_sentiment_scores(sentiments)

            if pos_sum > math.fabs(neg_sum):
                pos_sum += punct_emph_amplifier
            elif pos_sum < math.fabs(neg_sum):
                neg_sum -= punct_emph_amplifier

            total = pos_sum + math.fabs(neg_sum) + neu_count
            pos = math.fabs(pos_sum / total)
            neg = math.fabs(neg_sum / total)
            neu = math.fabs(neu_count / total)

        else:
            compound = 0.0
            pos = 0.0
            neg = 0.0
            neu = 0.0

        sentiment_dict = {
            "neg": round(neg, 3),
            "neu": round(neu, 3),
            "pos": round(pos, 3),
            "compound": round(compound, 4),
        }

        return sentiment_dict
