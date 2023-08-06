from kdmt.text import split_single
from kolibri import download
download('gazetteers')
import pandas as pd
from kolibri.tools.regexes import Regex
import re
from kolibri.task.text.entities.templated_extractor import TemplatedEntityExtractor
from kolibri.task.text.entities.person_extractor import PersonExtractor
from kolibri.task.text.entities.regex_extractor import RegexExtractor
from kolibri.task.text.entities.dictionaryExtractor import DictionaryExtractor
from kolibri.task.text.entities.common_reg_extractor import CommonRegexExtractor
import csv, json, operator
import ast



person_extractor = PersonExtractor()
# leave_types = DictionaryExtractor('leaveType', 'LeaveType')
# company_name = DictionaryExtractor('companyNames.csv', 'Company')


def extra_cleaning(text):
    pattern = r"\*-*-+[\s\w+:\/\.,\(\)]+\*-+"
    text = re.sub(pattern, "", text, re.UNICODE)
    pattern = r'\*?-{2,}'
    text = re.sub(pattern, "", text, re.UNICODE)

    pattern = r'[.\]*Received\s*:[\w /:@\.-]*Attachments\s*:'
    return re.sub(pattern, "", text, re.UNICODE)


def split_string(text):
    sentences = []
    sentences_ = split_single(text)
    for sentence in sentences_:
        sentences.extend(re.split(regex_sentence_breakers, sentence))

    return sentences


def remove_overlap(entities):
    result = []
    current_start = -1
    current_stop = -1
    sorted_ents = [e for e in (sorted(entities, key=operator.attrgetter('start')))]

    for se in sorted_ents:
        if se.start > current_stop:
            # this segment starts after the last segment stops
            # just add a new segment
            result.append(se)
            current_start, current_stop = se.start, se.end
        else:
            current_entity = result[-1]

            if current_entity.type in ['City', 'Money', 'Person', 'Country']:
                result[-1] = se

            # current_start already guaranteed to be lower
            current_stop = max(current_stop, se.end)

    return result


def update_text_data(full_text, sents_ents):
    ents = []
    search_from = 0
    for se in sents_ents:
        start_index = se['sentence'][1]

        for entity in se['entities']:
            entity.start += start_index
            entity.end += start_index
            ents.append(entity)

    remove_overlap(ents)

    return {"text": full_text, "entities": ents}


def get_entities_for_sentence(sentence):
    entities = []
    #        print(sent)
    #        entities.extend(template_extractor.process(sent))
    #        print(sent)
    #        if len(entities) == 0:
    persons = person_extractor.get_entities(sentence[0])
    if len(persons) > 0:
        entities.extend(persons)
    for entity in entities:
        entity.start += sentence[1]
        entity.end += sentence[1]
    return {"sentence": sentence, "entities": entities}





text = """Information Classification: ll Limited Access\nTicket C6B-1025769\nGood morning,\nAs part of the Employee Relations team I am approving employee Michelle Murphy's (567391) request for a personal LOA per the above referenced ticket.\nI did not see the request form attached to the ticket.\nEmployee referenced it during our conversation.\nMichelle's LOA can be approved through Sept 2nd, with a return to work date of September 3, 2019.\nShe has indicated that she has exhausted her vacation time so this will be unpaid.\nPlease let me know if you have questions or need anything else from me.\n
"""

print(get_entities_for_sentence(text))
