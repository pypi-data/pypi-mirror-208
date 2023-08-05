# -*- coding: utf-8 -*-
# !/usr/bin/env python

import regex as re
import csv

from kolibri.tools.scanner import Scanner
from kolibri.core.entity import Entity, Entities
from kolibri.tools import regexes

escapechars = '.\()[]?<!*+'


class TemplatedEntityExtractor(Scanner):
    """ Simple JavaScript tokenizer using the Scanner class"""

    def __init__(self, regexFile):

        super(TemplatedEntityExtractor, self).__init__(regexes)
        self.regex_data = csv.DictReader(open(regexFile))
        self.keywords = []
        self.entities = Entities()
        self.entityTypes = []
        self.regexSeparator = []
        self.regexEntity = []
        self.all_regexes = {}
        self.regexes = {}

        for r in self.regex_data:
            regex = {}

            self.keywords.append(r['Keyword'])
            if r['ReEntity'].strip() == 'string':
                pattern = regexes.string.pattern
            elif r['ReEntity'].strip() == 'date':
                pattern = regexes.date.pattern
            elif r['ReEntity'].strip() == 'person':
                pattern = regexes.person.pattern
            elif r['ReEntity'].strip() == 'money':
                pattern = regexes.money.pattern
            elif r['ReEntity'].strip() == 'phone':
                pattern = regexes.phone.pattern
            elif r['ReEntity'].strip() == 'email':
                pattern = regexes.email.pattern
            elif r['ReEntity'].strip() == 'address':
                pattern = regexes.street_address.pattern
            elif r['ReEntity'].strip() == 'number':
                pattern = regexes.number.pattern
            elif r['ReEntity'].strip() == 'code':
                pattern = regexes.code.pattern
            elif r['ReEntity'].strip() == 'period':
                pattern = regexes.period.pattern
            elif r['ReEntity'].strip() == 'social_security_number':
                pattern = regexes.social_security_nbr.pattern
            else:
                pattern = r['ReEntity'].strip()

            regex['patterns'] = u'({})({})({})'.format(self.escape(r['Keyword']).replace(' ', '_'),
                                                       r['ReSeparator'].strip(), pattern)

            regex['Entity'] = r['Entity'].strip()
            regex['EntityType'] = r['EntityType'].strip()
            regex['keyword'] = r['Keyword'].strip()
            regex['KeywordReg'] = r'(?<!_)\b{}{}'.format(self.escape(r['Keyword']), r['ReSeparator'].strip())
            regex['CleanKeyword'] = ' <' + r['Keyword'].replace(' ', '_') + ': '

            self.all_regexes[r['Keyword']] = regex

    def escape(self, pattern):
        for char in pattern:
            if char in escapechars:
                pattern = pattern.replace(char, "\\" + char)
        return pattern

    def prepare(self, src):
        self.regexes = {}
        for reg in self.all_regexes.values():
            if reg['keyword'] in src:
                self.regexes[reg['keyword']] = reg
                src = re.sub(reg['KeywordReg'], reg['CleanKeyword'], src)
        return src

    def process(self, src):

        self.entities = Entities()
        self.src = src
        self.string = self.prepare(src)
        nb_tags = 1
        nb_newlines = 1
        while not self.eos():
            """ Scanning is pretty simple in theory: we iterate over the string and
      say 'does this match here?... well how about this? ... ' etc
      
      It pays to do string based checks (isspace, isalpha, etc) before running
      regex methods (scan, check, skip), if possible
      """

            self.counter = 0

            index = self.pos
            c = self.peek()
            if c == '\n':
                nb_newlines += 1
            if c == '<':
                nb_tags += 1
                self.get()
                for reg in self.regexes.values():
                    if self.scan(reg['patterns'], re.UNICODE | re.IGNORECASE):
                        tok = reg['Entity']
                        value = self.string[index + len(reg['CleanKeyword']) - 2:self.pos].strip()
                        real_index = index - 2 * nb_tags - nb_newlines
                        real_index = self.src.index(value, real_index if real_index >= 0 else 0)

                        self.addEntity(tok, value, real_index)
                        break
            self.get()

        return self.entities

    def addEntity(self, tok, value, start):

        t = Entity(tok, value.strip(), start, start + len(value))
        t.idx = self.counter
        self.counter += 1
        self.entities.addEntity(t)


if __name__ == '__main__':

    text = """PThe funds have been debited from the account.

[ID:10096971 ]*APPROVED* 07.2019 Czech Rep
Dear Treasury Team,
Please note that July 2019payroll for AbbVie s.r.o. in Czech Republic has been approved by AbbVie.
Kindly secure the funds as per the tables below:
Bank file for Salaries:
Payroll Country:
Czech Republic
SAP Company Code:
6804 - AbbVie s.r.o.
Total amount to be paid:
CZK 5,082,407
Value Date:
02nd August 2019
Number of Transactions:
85
Cross Border Payment:
Payroll Country:
Czech Republic
SAP Company Code:
6804 - AbbVie s.r.o.
Total amount to be paid:
CZK 7,993.00
Value Date:
02nd August 2019
Number of Transactions:
1
Bank file for Authorities:
Payroll Country:
Czech Republic
SAP Company Code:
6804 - AbbVie s.r.o.
Total amount to be paid:
CZK 4,684,142
Value Date:
02nd August 2019
Number of Transactions:
8
TOTAL AMOUNT TO BE PAID:  9,774,542.00 CZK

*PLEASE APPROVE* 07.2019 Czech Rep
Hello,
Thank you. The payments are approved.
Please see audit forms attached.

*PLEASE APPROVE* 07.2019 Czech Rep
Importance: High
Hi Magda,
Please note thatJuly 2019 payroll for AbbVie s.r.o. in Czech Rep has been approved.
Can you please provide your approval for the following payments:
Bank file for Salaries:
Payroll Country:
Czech Republic
SAP Company Code:
6804 - AbbVie s.r.o.
Total amount to be paid:
CZK 5,082,407
Value Date:
02nd August 2019
Number of Transactions:
85
Cross Border Payment:
Payroll Country:
Czech Republic
SAP Company Code:
6804 - AbbVie s.r.o.
Total amount to be paid:
CZK 7,993.00
Value Date:
02nd August 2019
Number of Transactions:
1
Bank file for Authorities:
Payroll Country:
Czech Republic
SAP Company Code:
6804 - AbbVie s.r.o.
Total amount to be paid:
CZK 4,684,142
Value Date:
02nd August 2019
Number of Transactions:
8
TOTAL AMOUNT TO BE PAID:  9,774,542.00 CZK
Supporting documentation attached;
- bank files for salaries, payments to authorities, cross boarder payment
- bank file audit forms (salaries + authorities)
- final PY report (TPC)
- updated checklist
Any questions please let me know.4"""

    extractor = TemplatedEntityExtractor(
        "/Users/mbenhaddou/Documents/Mentis/Developement/Python/Kolibri/data/nga/ressources/entities_Descriptions.csv")
    entities = extractor.process(text)
    for ent in entities:
        print(ent.value, ent.type)
