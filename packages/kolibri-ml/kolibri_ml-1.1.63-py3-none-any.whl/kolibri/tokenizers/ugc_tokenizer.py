


import html
from typing import List
from kolibri.tokenizers.tokenizer import Tokenizer
from kolibri.tools import regexes as reg_lib
import regex
from kdmt.html import replace_html_entities
# The components of the tokenizer:

if reg_lib.HAS_REGRXES:
    REGEXPS = (
        reg_lib.URL.pattern,
        # ASCII Emoticons
        reg_lib.EMOTICONS.pattern,
        # HTML tags:
        r"""<[^>\s]+>""",
        # ASCII Arrows
        r"""[\-]+>|<[\-]+""",
        # Twitter username:
        r"""(?:@[\w_]+)""",
        # Twitter hashtags:
        r"""(?:\#+[\w_]+[\w\'_\-]*[\w_]+)""",
        # email addresses
        r"""[\w.+-]+@[\w-]+\.(?:[\w-]\.?)+[\w-]""",
        # Zero-Width-Joiner and Skin tone modifier emojis
        """.(?:[\\U0001F3FB-\\U0001F3FF]?(?:\\u200d.[\\U0001F3FB-\\U0001F3FF]?)+|[\\U0001F3FB-\\U0001F3FF])""",
        # Remaining word types:
        # Words with apostrophes or dashes.
        r"""(?:[^\W\d_](?:[^\W\d_]|['\-_])+[^\W\d_])""",
        # Numbers, including fractions, decimals.
        r"""(?:[+\-]?\d+[,/.:-]\d+[+\-]?)""",
        # Words without apostrophes or dashes.
        r"""(?:[\w_]+)""",
        # Ellipsis dots.
        r"""(?:\.(?:\s*\.){1,})""",
        # Everything else that isn't whitespace.
        r"""(?:\S)""",
    )

    EMOTICON_RE = regex.compile(reg_lib.EMOTICONS.pattern, regex.VERBOSE | regex.I | regex.UNICODE)

######################################################################
# TweetTokenizer.WORD_RE and TweetTokenizer.PHONE_WORD_RE represent
# the core tokenizing regexes. They are compiled lazily.

# WORD_RE performs poorly on these patterns:
HANG_RE = regex.compile(r"([^a-zA-Z0-9])\1{3,}")

# The emoticon string gets its own regex so that we can preserve case for
# them as needed:



# For stripping away handles from a tweet:
HANDLES_RE = regex.compile(
    r"(?<![A-Za-z0-9_!@#\$%&*])@"
    r"(([A-Za-z0-9_]){15}(?!@)|([A-Za-z0-9_]){1,14}(?![A-Za-z0-9_]*@))"
)



class UGCTokenizer(Tokenizer):
    r"""
    Tokenizer for tweets.

        >>> from kolibri.tokenizers import UGCTokenizer
        >>> tknzr = UGCTokenizer()
        >>> s0 = "This is a cooool #dummysmiley: :-) :-P <3 and some arrows < > -> <--"
        >>> tknzr.tokenize(s0)
        ['This', 'is', 'a', 'cooool', '#dummysmiley', ':', ':-)', ':-P', '<3'
        , 'and', 'some', 'arrows', '<', '>', '->', '<--']

    Examples using `strip_handles` and `reduce_len parameters`:

        >>> tknzr = UGCTokenizer(strip_handles=True, reduce_len=True)
        >>> s1 = '@remy: This is waaaaayyyy too much for you!!!!!!'
        >>> tknzr.tokenize(s1)
        [':', 'This', 'is', 'waaayyy', 'too', 'much', 'for', 'you', '!', '!', '!']
    """

    # Values used to lazily compile WORD_RE and PHONE_WORD_RE,
    # which are the core tokenizing regexes.
    _WORD_RE = None
    _PHONE_WORD_RE = None

    ######################################################################

    defaults = {
        "fixed":{
            "reduce-len": False,
            "strip-handles": False,
            "match-phone-numbers" : True
        },
        "tunable":{}
    }
    def __init__(self, configs={}):
        """
        Create a `TweetTokenizer` instance with settings for use in the `tokenize` method.

        :param preserve_case: Flag indicating whether to preserve the casing (capitalisation)
            of text used in the `tokenize` method. Defaults to True.
        :type preserve_case: bool
        :param reduce_len: Flag indicating whether to replace repeated character sequences
            of length 3 or greater with sequences of length 3. Defaults to False.
        :type reduce_len: bool
        :param strip_handles: Flag indicating whether to remove Twitter handles of text used
            in the `tokenize` method. Defaults to False.
        :type strip_handles: bool
        :param match_phone_numbers: Flag indicating whether the `tokenize` method should look
            for phone numbers. Defaults to True.
        :type match_phone_numbers: bool
        """

        super().__init__(parameters=configs)
        self.preserve_case = not self.get_parameter("do-lower-case")
        self.reduce_len = self.get_parameter("reduce-len")
        self.strip_handles = self.get_parameter("strip-handles")
        self.match_phone_numbers = self.get_parameter("match-phone-numbers")

    def tokenize(self, text: str) -> List[str]:
        """Tokenize the input text.

        :param text: str
        :rtype: list(str)
        :return: a tokenized list of strings; joining this list returns\
        the original string if `preserve_case=False`.
        """
        # Fix HTML character entities:
        text = replace_html_entities(text)
        # Remove username handles
        if self.strip_handles:
            text = remove_handles(text)
        # Normalize word lengthening
        if self.reduce_len:
            text = reduce_lengthening(text)
        # Shorten problematic sequences of characters
        safe_text = HANG_RE.sub(r"\1\1\1", text)
        # Recognise phone numbers during tokenization
        words = self.WORD_RE.findall(safe_text)
        # Possibly alter the case, but avoid changing emoticons like :D into :d:
        if not self.preserve_case:
            words = list(
                map((lambda x: x if EMOTICON_RE.search(x) else x.lower()), words)
            )
        return words

    @property
    def WORD_RE(self) -> "regex.Pattern":
        """Core TweetTokenizer regex"""
        # Compiles the regex for this and all future instantiations of TweetTokenizer.
        if not type(self)._WORD_RE:
            type(self)._WORD_RE = regex.compile(
                f"({'|'.join(REGEXPS)})",
                regex.VERBOSE | regex.I | regex.UNICODE,
            )
        return type(self)._WORD_RE

    @property
    def PHONE_WORD_RE(self) -> "regex.Pattern":
        """Secondary core TweetTokenizer regex"""
        # Compiles the regex for this and all future instantiations of TweetTokenizer.
        if not type(self)._PHONE_WORD_RE:
            type(self)._PHONE_WORD_RE = regex.compile(
                f"({'|'.join([pattern.pattern for pattern in reg_lib.PHONE_NUMBER.values()])})",
                regex.VERBOSE | regex.I | regex.UNICODE,
            )
        return type(self)._PHONE_WORD_RE


######################################################################
# Normalization Functions
######################################################################


def reduce_lengthening(text):
    """
    Replace repeated character sequences of length 3 or greater with sequences
    of length 3.
    """
    pattern = regex.compile(r"(.)\1{2,}")
    return pattern.sub(r"\1\1\1", text)


def remove_handles(text):
    """
    Remove Twitter username handles from text.
    """
    # Substitute handles with ' ' to ensure that text on either side of removed handles are tokenized correctly
    return HANDLES_RE.sub(" ", text)


