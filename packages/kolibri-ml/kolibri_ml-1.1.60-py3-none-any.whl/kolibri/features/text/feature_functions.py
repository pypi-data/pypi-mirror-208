import re
import kolibri
from string import punctuation

def has_email(line, text=None, **Kwargs):
    o = re.findall(r'[\w\.-]+@[\w\.-]+', line)
    if "return_count" in Kwargs and Kwargs["return_count"]:
        return len(o)

    return len(o) > 0

def has_only_quotes(line, text=None, **Kwargs):
    o = re.findall(r'^[\s]*---*[\s]*$', line)
    if "return_count" in Kwargs and Kwargs["return_count"]:
        return len(o)

    return len(o) > 0

def contains_phone(line, text=None, **Kwargs):
    o = re.findall(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', line)
    if "return_count" in Kwargs and Kwargs["return_count"]:
        return len(o)

    return len(o) > 0

# def count_named_entities(line, text=None, **Kwargs):
#     return
#     entities_count = 0
#     for sent in kolibri.tokenize_sentences(line):
#         for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
#             if hasattr(chunk, 'label'):
#                 entities_count += 1
#
#     if entities_count > 0:
#         return entities_count
#     return False

def is_in_last_n_lines(line, text=None, **Kwargs):
    if "n" in Kwargs:
        n=Kwargs["n"]
    else:
        n=1
    try:
        lines = [l.strip() for l in text if len(l) > 0]
        line_index = max([i for i, l in enumerate(lines) if line in l])
        output = True if len(lines) - (n+1) < line_index else False
    except:
        output = False
    return output

def is_in_second_half(line, text=None, **Kwargs):
    idx=-1
    try:
        idx = text.index(line.strip())
    except:
        pass

    if idx > len(text)/2:
        return True
    return False

def contains_word_from_list(line, text=None, **Kwargs):
    list=[]
    if "list" in Kwargs:
        list=Kwargs["list"]

    o = re.findall("|".join(list),
        line)
    return len(o) > 0

def has_url(line, text=None, **Kwargs):
    url_regex = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
    o = re.findall(url_regex, line)
    if "return_count" in Kwargs and Kwargs["return_count"]:
        return len(o)
    return len(o) > 0

def has_numbers(line, text=None, **Kwargs):
    """ Function to count the number of numbers appearing in a
        passage of line.
    """
    results = re.findall(r'\b[,0-9\.]+', line)
    results = [result for result in results
                if not re.match(r'(199|20[01])\d', result)
                  and re.search(r'[0-9]', result)]
    if "return_count" in Kwargs and Kwargs["return_count"]:
        return len(results)

    return len(results)>0

def word_count(line, text=None, **Kwargs):
    return len(str(line).split(" "))

def char_count(line, text, return_count=False):
    return len (line)

def avg_word_length(line, text=None, **Kwargs):
    words = line.split()
    return (sum(len(word) for word in words) / len(words))

def has_hashtags(line, text=None, **Kwargs):
    o= len([x for x in line.split() if x.startswith('#')])

    if "return_count" in Kwargs and Kwargs["return_count"]:
        return len(o)

    return len(o) > 0

def has_user_mentions(line, text=None, **Kwargs):
    o= len([x for x in line.split() if x.startswith('@')])
    if "return_count" in Kwargs and Kwargs["return_count"]:
        return len(o)

    return len(o) > 0

def count_punc(line, text=None, **Kwargs):
    """
    Count the number of punctuations within the line.

    Parameters
    ----------
    line : str
        piece of line to analyze
    Returns
    -------
    integer
        the number of punctuations
    Examples
    --------
    >>> count_punc("Hello, World!")
    2
    >>> count_punc("Hello World")
    0
    """
    if not isinstance(line, str):
        raise TypeError("'line' should be of type 'String'")
    count = 0
    for ch in line:
        if ch in punctuation:
            count += 1
    return count

# Count percentage of fully capitalised words
def has_cap_words(line, text=None, **Kwargs):
    """
    Calculate percentage of fully capitalised words in the line.
    Parameters
    ----------
    line : str
        the input line

    Returns
    -------
    float
        percentage of capitalised words

    Examples
    --------
    >>> perc_cap_words("THIS is a SPAm MESSage.")
    20
    >>> perc_cap_words("THIS is a SPAM MESSAGE.")
    60
    """
    if line == " " or line == "":
        raise TypeError("'line' should not be empty!")
    if not isinstance(line, str):
        raise TypeError("'line' should be of type 'String'")

    count_cap_words = 0  # Initialises the count for the number of capitalised words
    words = line.split(' ')  # Splits the string based on spaces
    for word in words:
        if word.isupper():
            count_cap_words += 1  # Adds one to the count if the entire word is uppercase

    if "return_count" in Kwargs and Kwargs["return_count"]:
        return count_cap_words

    if "return_percent" in Kwargs and Kwargs["return_percent"]:
        return (count_cap_words / len(words) * 100)

    return count_cap_words > 0

def has_title_words(line, text=None, **Kwargs):
    """
    Calculate percentage of fully capitalised words in the line.
    Parameters
    ----------
    line : str
        the input line

    Returns
    -------
    float
        percentage of capitalised words

    Examples
    --------
    >>> perc_cap_words("THIS is a SPAm MESSage.")
    20
    >>> perc_cap_words("THIS is a SPAM MESSAGE.")
    60
    """
    if line == " " or line == "":
        raise TypeError("'line' should not be empty!")
    if not isinstance(line, str):
        raise TypeError("'line' should be of type 'String'")

    count_cap_words = 0  # Initialises the count for the number of capitalised words
    words = line.split(' ')  # Splits the string based on spaces
    for word in words:
        if word.istitle():
            count_cap_words += 1  # Adds one to the count if the entire word is uppercase

    if "return_count" in Kwargs and Kwargs["return_count"]:
        return count_cap_words

    if "return_percent" in Kwargs and Kwargs["return_percent"]:
        return (count_cap_words / len(words) * 100)

    return count_cap_words > 0





if __name__ == '__main__':

    list=["Fox", "Dog"]
    text=["The Fox jump over the lasy","http://www.ibm.com @mbenhaddou", "#jboom, http://www.ibm.be"]

    line="The FOX Nnumber 2 jump over the lasy DOG number 3"

    print(has_title_words(line, text, return_percent=True))