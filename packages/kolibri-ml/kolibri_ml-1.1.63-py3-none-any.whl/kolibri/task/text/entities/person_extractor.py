from kolibri.tools.keywords import KeywordProcessor
from kolibri.tokenizers.kolibri_tokenizer import KolibriTokenizer
from kolibri.core.entity import Entity
from kolibri.task.text.entities.dictionaryExtractor import DictionaryExtractor
import os
import regex as re
from kolibri.data import find
person_file_name = find('packages/gazetteers/default/first_name.txt')
keyword_exception_file_name= find('packages/gazetteers/default/name_exceptions.txt')


class PersonExtractor(DictionaryExtractor):
    def __init__(self, case_sensitive=False):
        DictionaryExtractor.__init__(self, person_file_name, 'Person', case_sensitive=case_sensitive)
        self.tokenizer = KolibriTokenizer({"outout-type": "tokens"})
        self.exceptions=set(line.strip() for line in open(keyword_exception_file_name))
        self.keyword_exception_regex_start ='|'.join(self.exceptions)
    def get_entities(self, text):
        #    print(d)
        tokens = self.tokenizer.tokenize(text)

        persons = self.keywords.extract_keywords(text, True)


        # print(persons)

        FinalPersonns = []
        j = 0
        for person in persons:
            start = person[1]
            for i in range(j, len(tokens)):
                if start >= tokens[i].start and start < tokens[i].end:
                    if tokens[i].get('type') in ['CANDIDATE']:
                        FinalPersonns.append(Entity(self.type, tokens[i].text, tokens[i].start, tokens[i].end))
                    elif i < len(tokens) - 1 and tokens[i + 1].get('type') in ['CANDIDATE'] and tokens[i].get('type') in ['WORD', 'ACRONYM']:
                        candidate=tokens[i].text + ' ' + tokens[i + 1].text
                        FinalPersonns.append(
                                Entity(self.type, candidate, tokens[i].start,
                                       tokens[i + 1].end))
                    j = i + 1
        employeeids = []

        for person in FinalPersonns:

            person.value = re.sub(r"^(Hi|Hello|Dear|However|For|If|Employees?|"+self.keyword_exception_regex_start+")\s", '', person.value)
            person.start = person.end - len(person.value)
            person.value = re.sub(r"'s$", '', person.value)
            person.end = person.start + len(person.value)
            #Apply twice ToDO: find a better approach
            person.value = re.sub(r"^(Hi|Hello|Dear|However|For|If|Employees?|"+self.keyword_exception_regex_start+")\s", '', person.value)
            person.start = person.end - len(person.value)


            person.value = re.sub(r"(Hi|Hello|Dear|However|For|If|Employees?|"+self.keyword_exception_regex_start+")$", '', person.value)
            person.end = person.start + len(person.value)


            pattern = re.escape(
                person.value) + r"[\s\(\[#]*(?P<EmployeeId>e?\d{5,8}\b)|\b(?P<EmployeeId>e?\d{5,8}\b)[\s\)\]#]*" + re.escape(
                person.value)
            matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                for group, index in zip(match.groups(), range(0, len(match.group()))):
                    if group is not None:
                        employeeids.append(
                            Entity("EmployeeId", group, match.start(index + 1), match.end(index + 1)))

        FinalPersonns.extend(employeeids)
        return FinalPersonns


if __name__ == '__main__':
    text = """Oct 2019 Unilever HRO PM10 JDC RIce Allowance Krystel Nicole Tan\nTeam,\nPlease see attached file"""
    pe = PersonExtractor(False)

    entities = pe.get_entities(text)

    for e in entities:
        print(e.tojson())
