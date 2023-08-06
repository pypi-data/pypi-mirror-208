# -*- coding: utf-8 -*-
# !/usr/bin/env python
import datetime

import regex as re
import collections
from kolibri.preprocess.text.cleaning.cleaning_scripts import fix_email_formatting, clean
from kolibri.preprocess.text.cleaning.__email_configs import *
from kolibri.preprocess.text.language_detection import detect_language
import dateparser
from kolibri.preprocess.text.cleaning.header_parser import HeaderParser

import glob
from os.path import join
from tqdm import tqdm
import os
import pytz
from kolibri.preprocess.text.cleaning.email_parser import parse_eml
class EmailMessage(object):
    """
    An email message represents a parsed email body.
    """

    def __init__(self, language='en', split_pattern=None, remove_html=True, escape_rejected_emails=True, detect_outof_office=True):
        self.date = None
        self.fragments = []
        self.fragment = None
        self.found_visible = False
        self.language = language
        self.salutations = salutation_opening_statements

        self.split_pattern = split_pattern
        self.regex_header = r"|".join(regex_headers)
        self.subject=""
        self.sender=None
        self.email_parser=None
        self.parsed_data={}
        self.remove_html=remove_html
        self.escape_rejected_emails=escape_rejected_emails
        self.detect_out_of_office=detect_outof_office
    def read(self, body_text, sender=None, date=None, title_text=None, collated_text=False, parse_dates=False, date_format="%Y-%m-%d %H:%M:%S"):
        """ Creates new fragment for each line
            and labels as a signature, quote, or hidden.
            Returns EmailMessage instance
        """
        self.fragments = []
        self.subject=str(title_text)
        self.sender=sender
        try:
            date_ = dateparser.parse(date, date_formats=[date_format])
            self.date = date_


            if self.date.tzinfo is None:
                self.date = pytz.utc.localize(self.date)

        except Exception as e:
            self.date=date

        body_text=clean(str(body_text), remove_html=self.remove_html)
        body_text=fix_email_formatting(body_text)

        self.source_text=body_text
        message=""
        if self.escape_rejected_emails:
            for rejection in rejected_emails_formulas:
                if re.findall(rejection.strip(), body_text):
                    message="[EMAIL_REJECTED]"
                    break

        if self.detect_out_of_office:
            for ooo in ooo_emails_formulas:
                if re.findall(ooo.strip(), body_text):
                    message = "[OOO]"
                    break
        self.text=body_text
        if message=="[EMAIL_REJECTED]":
            fragment=Fragment(body_text, self.salutations, self.regex_header, parse_dates=parse_dates)
            fragment.is_rejected=True
            self.fragments.append(fragment)
            return self
        elif message== "[OOO]":
            fragment=Fragment(body_text, self.salutations, self.regex_header)
            fragment.is_out_of_office=True
            self.fragments.append(fragment)
            return self
        self.subject = str(title_text)
        #        regex_header = r"(From|To)\s*:[0-9A-Za-zöóìśćłńéáú⺀-⺙⺛-⻳⼀-⿕々〇〡-〩〸-〺〻㐀-䶵一-鿃豈-鶴侮-頻並-龎\s\/@\.:,;\&\?\\\(\)'\"\*[\]<>#\/\+_-]+?((Subj(ect)?)|Sent at)\s?:|From\s*:[\w @\.:,;\&\(\)'\"\*[\]<>#\/\+-]+?(Sent|Date)\s?:(\s*\d+(\s|\/)(\w+|\d+)(\s|\/)\d+(\s|\/)?(\d+:\d+)?)?|From\s*:[\w @\.:,;\&\(\)'\"\*[\]<>#\/\+-]+?(Sent\s+at)\s?:(\s*\d+\s\w+\s\d+\s?\d+:\d+)?|From\s*:[\w @\.:,;\&\?\\\(\)'\"\*[\]<>#\/\+-]+?(CC)\s?:|From\s*:[\w @\.:,;\&\?\\\(\)'\"\*[\]<>#\/\+-]+?(To)\s?:|(De|Da)\s*:[0-9ÀA-Za-zéàçèêù\s\/@\.:,;\&\?\\\(\)'\"\*[\]<>#\/\+-]+(Objet|Oggetto)\s?:"
        if self.split_pattern:
            self.regex_header = r"" + self.split_pattern
        starts = [m.start(0) for m in re.finditer(self.regex_header, self.text, re.MULTILINE | re.UNICODE)]

        if len(starts) < 1:
            if collated_text:
                starts = [m.start(0) for m in re.finditer(pattern_salutation_colated, self.text, re.MULTILINE)]
            else:
                starts = [m.start(0) for m in re.finditer(pattern_salutation, self.text, re.MULTILINE)]

            starts = [s for s in starts if s > 150]
        if len(starts) < 1:
            fragment=Fragment(self.text, self.salutations, self.regex_header, collated_text)
            if fragment.date is None:
                fragment.date = self.date
            if fragment.sender is None:
                fragment.sender = self.sender
            self.fragments.append(fragment)

        else:
            if starts[0] > 0:
                starts.insert(0, 0)
            lines = [self.text[i:j] for i, j in zip(starts, starts[1:] + [None])]

            for line in lines:
                if self.split_pattern:
                    line = re.sub(self.split_pattern, '', line)
                if line.strip() != '':
                    fragment=Fragment(line, self.salutations, self.regex_header, collated_text)
                    if fragment.date is None:
                        fragment.date=self.date
                    if fragment.sender is None:
                        fragment.sender=self.sender

                    self.fragments.append(fragment)
        #sort by date
#        try:
#            self.fragments=sorted(self.fragments, key=lambda x: x.date)
#        except:
#            pass
        return self

    def read_eml(self, eml_file):
        self.parsed_data= parse_eml(eml_file)
        self.read(self.parsed_data['body'], self.parsed_data['title'])
        if self.fragments[0].date is None:
            self.fragments[0].date=self.parsed_data["date"]
        return self

    def get_main_fragments(self, min_message_length=20):
        """
        Prioritize the fragment to be returned as main based on huristics.
        :return:
        """
        if self.subject[:3]=='FW:' and len(self.fragments)>=2:
            if len(self.fragments[0].body.strip())>0:
                return [self.fragments[0], self.fragments[1]]
            else:
                return [self.fragments[1]]
        for fragment in self.fragments:
            if len(fragment.body)>=min_message_length:
                return [fragment]
        return [self.fragments[0]]


    def detect_language(self):

        langs = [l.language for l in self.fragments]
        languages = collections.Counter()
        for d in langs:
            languages.update(d)
        if not languages:
            try:
                lang = detect_language(self.text, num_laguages=2)
            except Exception  as e:
                languages['und'] = 0.90
                print(e)
                return languages

            for l in lang:
                languages[l.language] = l.probability
        self.language=max(languages, key=languages.get)
        return self.language


class Fragment(object):
    """ A Fragment is a part of
        an Email Message, labeling each part.
    """

    def __init__(self, email_text, salutations, regex_header, collated_text=False, parse_dates=False):
        self.collated_text=collated_text
        self.parse_dates=parse_dates
        self.salutations = salutations
        self.body = email_text.strip()
        self.regex_header = regex_header
        self.is_forwarded_message = self._get_forwarded()
        self.is_out_of_office=False
        self.is_rejected=False
        self.subject = None
        self.sender=None
        self.date=None
        self.headers = self._process_header()
        self.caution = self._get_caution_or_front_content()
        if self.subject is None and not self.collated_text:
            self.subject = self._get_title()
        self.attachement = self._get_attachement()
        self.salutation = self._get_salutation()
        self.disclaimer = self._get_disclaimer()
        self.signature = self._get_signature()
        self._content = email_text


    def _get_title(self):
        patterns = [
            "(R[Ee]|Antw\.:|F[Ww])\s?:\s?.+",
            ".*\s+(?=(Hi|Hello|Dear))"
        ]

        pattern = r'(?P<title>(' + '|'.join(patterns) + '))'
        groups = re.match(pattern, self.body)
        title = ""
        if groups is not None:
            if "title" in groups.groupdict().keys():
                title = groups.groupdict()["title"]
                self.body = self.body[len(title):].strip()
        return title

    def _get_caution_or_front_content(self):
        patterns =[c.strip() for c in email_caution_or_fron_content+sent_from_my_device if c.strip()]
#        pattern = r'(?P<caution>^\s*(' + r'|'.join(regexes) + '))'
        pattern=r'(?P<caution>^\s*(^\s*'+ r'|'.join(patterns)+'))'

        match = re.search(pattern, self.body)
        cautions = []
        while match:
            caution = match.group()
            cautions.append(caution)
            _span = match.span()
            self.body=self.body[_span[1]:]
            match = re.search(pattern, self.body)
#        start_with_closing=
        if len(cautions)==0:
            start_with_closing= re.match(signature_pattern_bis, self.body.strip())
            if start_with_closing:
                #we search for salution. if email start with closing, then form closing to salutation is to be removed
                match= re.search(pattern_salutation, self.body, re.MULTILINE)
                if match:
                    cautions = self.body[:match.start()]
                    self.body=self.body[match.start():]
            return cautions
        # groups = re.match(pattern, self.body, re.MULTILINE)
        # caution=""
        # if groups is not None:
        #     if "caution" in groups.groupdict().keys():
        #         caution = groups.groupdict()["caution"]
        #         self.body = self.body[len(caution):].strip()
        return '\n'.join(cautions)

    def _get_attachement(self):
        pattern = r'(?P<attachement>(^\s*[a-zA-Z0-9_,\. -]+\.(png|jpeg|docx|doc|xlsx|xls|pdf|pptx|ppt))|Attachments\s?:\s?([a-zA-Z0-9_,\. -]+\.(png|jpeg|docx|doc|xlsx|xls|pdf|pptx|ppt)))'
        groups = re.match(pattern, self.body, re.IGNORECASE)
        attachement = ''
        if not groups is None:
            if "attachement" in groups.groupdict().keys():
                attachement = groups.groupdict()["attachement"]
                self.body = self.body[len(attachement):].strip()
        return attachement

    def _get_salutation(self):
        # Notes on regex:
        # Max of 5 words succeeding first Hi/To etc, otherwise is probably an entire sentence

        groups = re.match(pattern_salutation, self.body)
        salutation = ''
        if groups is not None:
            if "salutation" in groups.groupdict().keys():
                salutation = groups.groupdict()["salutation"]
                self.body = self.body[len(salutation):].strip()
        return salutation

    @property
    def language(self):
        return_val = {}
        regx = "\*?-+\s+Sent\s+:.*\s+Received\s+:.*\s+Reply to\s:.*\s+Attachments\s+:.*\s+\*?-*|Dear Sender, thank you for your e-mail. I'll be out of office until.*|NO BODY.*|[^\w.,:\s]"
        text = self.body
        text = re.sub(regx, ' ', text.strip())



        return detect_language(text, num_languages=2, use_large_model=True)

    def _process_header(self):
        header_parser=HeaderParser(self.parse_dates)

        he=header_parser.parse(self.body)
        if he:
            self.body=header_parser.body
            self.date=he.get('Date_parsed', None)
            if self.date is not None:
                try:
                    self.date = pytz.utc.localize(self.date)
                except Exception as e:
                    pass
            self.date_str=str(he.get('Date', None))
            self.sender=he.get('From', None)
            self.reciever=he.get('To', None)
            self.subject=he.get("Subject", None)

#         print(self.body)
#         print('---------------------')
#
#
#         header_parser=HeaderParser()
#
#         he=header_parser.parse(self.body)
#         if he!={}:
#             print(he)
#         print('-----------------')
# #        print(header_parser.body)
#         #        regex = r"From\s*:[\w @\.:,;\&\?\\\(\)'\"\*[\]<>#\/\+-]+?(Subj(ect)?)\s?:|From\s*:[\w @\.:,;\&\(\)'\"\*[\]<>#\/\+-]+?(Sent|Date)\s?:(\s*\d+(\s|\/)(\w+|\d+)(\s|\/)\d+(\s|\/)?(\d+:\d+)?)?|From\s*:[\w @\.:,;\&\(\)'\"\*[\]<>#\/\+-]+?(Sent\s+at)\s?:(\s*\d+\s\w+\s\d+\s?\d+:\d+)?|From\s*:[\w @\.:,;\&\?\\\(\)'\"\*[\]<>#\/\+-]+?(CC)\s?:|From\s*:[\w @\.:,;\&\?\\\(\)'\"\*[\]<>#\/\+-]+?(To)\s?:"
#
#         pattern = r"(?P<header_text>(" + self.regex_header + "))"
#
#         date_group = re.search(pattern, self.body)
#         header_text = None
#         if date_group is not None:
#             if "header_text" in date_group.groupdict().keys():
#                 header_text = date_group.groupdict()["header_text"]
#                 self.body = self.body[len(header_text):].strip()
#             if 'subject' in date_group.groupdict().keys():
#                 if not self.collated_text:
#                     self.title = date_group.groupdict()["subject"]
#                 elif date_group.groupdict()["subject"] is not None:
#                     self.body=date_group.groupdict()["subject"]+' '+self.body
#                     header_text=""
#
#         if header_text is not None:
#             date_group = re.search(header_date_regex, header_text, re.UNICODE | re.MULTILINE)
#             from_group = re.search(header_from_regex, header_text, re.UNICODE | re.MULTILINE)
#
#             if date_group:
#                 sent_text = date_group.groupdict()["date"]
# #                sent_text = re.sub(r'((?<=\s(\d{2})\:(\d{2})(\:\d{2}))|(?<=\s(\d{2})\:(\d{2}))|(?<=\s(\d{1})\:(\d{2}))).*|(,|\+\d)?\s*[<\w+:-_]+@[<\w+-_>]+.*', '', sent_text, re.IGNORECASE)
# #                 try:
# #                     date_=dateparser.parse(sent_text, date_formats=["%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M"])
# #                     if date_ is not None and date_.tzinfo is None:
# #                         date_=pytz.utc.localize(date_)
# #                     elif date_ is None:
# #                         print(header_text)
# #                 except:
# #                     raise
# #                 if date_ is not None:
# #                     self.date=date_
#
#             if from_group:
#                 from_text = from_group.groupdict()["from"]
#                 self.sender=from_text
#
#             # else:
#             #     print(header_text)
#         # else:
#         #     print("no_header")
#
#         return header_text

    def _get_disclaimer(self):

        groups = re.search(pattern_disclaimer, self.body, re.MULTILINE + re.DOTALL)
        disclaimer_text = None
        if groups is not None:
            if "disclaimer_text" in groups.groupdict().keys():
                found = groups.groupdict()["disclaimer_text"]
                disclaimer_text = self.body[self.body.find(found):]
                self.body = self.body[:self.body.find(disclaimer_text)].strip()

        return disclaimer_text

    def _get_signature(self):
        # note - these openinged statements *must* be in lower case for
        # sig within sig searching to work later in this func

        # TODO DRY
        self.signature = ''
        if self.collated_text:

            groups = re.search(signature_pattern_colated_text, self.body, re.IGNORECASE | re.MULTILINE)
        else:
            groups = re.search(signature_pattern, self.body, re.IGNORECASE | re.MULTILINE)
        signature = None
        if groups:
            if "signature" in groups.groupdict().keys():
                signature1 = groups.groupdict()["signature"]
                # search for a sig within current sig to lessen chance of accidentally stealing words from body
                sig_span = groups.span()
                if sig_span[0]<10:
                    return ""
                signature = self.body[sig_span[0]:]
                self.body = self.body[:sig_span[0]]
                groups = re.search(signature_pattern, signature[len(signature1):], re.IGNORECASE|re.MULTILINE)
                if groups:
                    signature2 = groups.groupdict()["signature"]
                    sig_span = groups.span()
                    if self.collated_text:
                        self.body = self.body + ' ' + signature[:len(signature1) + sig_span[0]]
                    else:
                        self.body = self.body + '\n' + signature[:len(signature1)+sig_span[0]]
                    signature = signature[len(signature1)+sig_span[0]:]
        else:
            groups = re.search(function_re, self.body, re.DOTALL)

            if groups is not None and "signature" in groups.groupdict().keys():
                signature = groups.groupdict()["signature"]
                # search for a sig within current sig to lessen chance of accidentally stealing words from body
                self.body = self.body[:self.body.find(signature)].strip()
        self.body=re.sub(r"^\s*[\*,;.?!_=+-]+", "", self.body)
        return signature

    def _get_forwarded(self):

        pattern = '(?P<forward_text>([- ]* Forwarded Message [- ]*|[- ]* Forwarded By [- ]*|[- ]*Original Message[- ]*))'
        groups = re.search(pattern, self.body, re.DOTALL)
        forward = None
        if groups is not None:
            if "forward_text" in groups.groupdict().keys():
                forward = groups.groupdict()["forward_text"]

        if forward is not None:
            self.body = self.body.replace(forward, '')

        return forward is not None

    @property
    def content(self):
        return self._content.strip()

def get_input_files(dir_path, type):

    return glob.glob(join(dir_path, "*." + type))


def process_eml_from_folder():

    import xlsxwriter

    workbook = xlsxwriter.Workbook('/Users/mohamedmentis/Dropbox/My Mac (MacBook-Pro.local)/Documents/Mentis/Clients/Octa+/octaplus.xlsx')
    worksheet = workbook.add_worksheet()

    files=get_input_files("/Users/mohamedmentis/Dropbox/My Mac (MacBook-Pro.local)/Desktop/data", 'eml')

    worksheet.write(0, 0, "ContactId")
    worksheet.write(0, 1, "body")
    worksheet.write(0, 2, "title")
    worksheet.write(0, 3, "from")
    worksheet.write(0, 4, "to")
    worksheet.write(0, 5, "date")
    worksheet.write(0, 6, "from_name")
    worksheet.write(0, 7, "language")
    worksheet.write(0, 8, "references")
    worksheet.write(0, 9, "in_replay_to")
    worksheet.write(0, 10, "attachement_names")
    worksheet.write(0, 11, "clean_body_first")
    worksheet.write(0, 12, "lang_body_first")
    worksheet.write(0, 13, "clean_body_concatenated")
    worksheet.write(0, 14, "lang_body_concatenated")
    worksheet.write(0, 15, "clean_body_last")
    worksheet.write(0, 16, "lang_body_last")



    i=1

    with tqdm(total=len(files), position=0, leave=True) as pbar:
        for  file in tqdm(files, position=0, leave=True):
            email=EmailMessage().read_eml(file)
#            cleaned='\n'.join([f.title + '\n' + f.body for f in email.fragments])
#            print(cleaned)
#            print('-----------------------------------------------------------------------\n')
            parsed=email.parsed_data
            parsed["FileName"]=os.path.split(file)[1]
            worksheet.write(i, 0, parsed["FileName"])
            worksheet.write(i, 1, parsed["body"])
            worksheet.write(i, 2, parsed["title"])
            worksheet.write(i, 3, parsed["from"])
            worksheet.write(i, 4, ";".join([ p for p in parsed["to"]]))
            worksheet.write(i, 5, str(parsed["date"]))
            worksheet.write(i, 6, parsed["from_name"])
            worksheet.write(i, 7, parsed["language"])
            worksheet.write(i, 8, ";".join([r for r in parsed["message-id"]]))
            worksheet.write(i, 9, ";".join([r for r in parsed["in_replay_to"]]))
            worksheet.write(i, 10, ";".join([a for a in parsed["attachement_names"]]))
            worksheet.write(i, 11,  email.fragments[0].body)
            worksheet.write(i, 12,  next(iter(email.fragments[0].language)) if email.fragments[0].language else next(iter(email.detect_language())))
            worksheet.write(i, 13,  '\n'.join([f.subject + '\n' + f.body for f in email.fragments]))
            worksheet.write(i, 14, next(iter(email.detect_language())))
            worksheet.write(i, 15,  email.fragments[-1].body)
            worksheet.write(i, 16,  next(iter(email.fragments[-1].language)) if email.fragments[-1].language else next(iter(email.detect_language())))

            i+=1
            pbar.update()

    workbook.close()


def clean_email(text,no_newLines=False):
    if text is None or text.strip()=='':
        return ''
    parsed=EmailMessage().read(body_text=text, title_text=None, collated_text=no_newLines)

    if parsed is  not None:
        return '\n'.join([f.body for f in parsed.fragments])


if __name__ == "__main__":
    # import cProfile, pstats, io
    # from pstats import SortKey
    #
    # pr = cProfile.Profile()
    # pr.enable()

#    process_eml_from_folder()
    # pr.disable()
    # s = io.StringIO()
    # sortby = SortKey.CUMULATIVE
    # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    # ps.print_stats()
    # print(s.getvalue())

    text="""Beste,
Op heden hebben wij nog geen verdere info ontvangen over onze inschrijving.
registratienummer WEG-17178
Dat zou normaal binnen de 5 werkdagen zijn dus vandaar deze mail.
Graag uw reactie. 
Met vriendelijke groeten,
Pieter-Jan Abeloos
0499 58 50 30
Abeloos Projects BV
Domeindreef 7
8200 Sint-Michiels
Van: Céline Van Maele <vanmaeleceline@gmail.com>
Verzonden: donderdag 8 september 2022 16:12
Aan: Pieter-Jan Abeloos <pieter-jan@abeloosprojects.be>
Onderwerp: Fwd: Bevestiging inschrijving OCTA+;
Begin doorgestuurd bericht: Van: energie@octaplus.be
Datum: 8 september 2022 om 15:43:31 CEST
Aan: vanmaeleceline@gmail.com
Onderwerp: Bevestiging inschrijving OCTA+;
Antwoord aan: Energie@octaplus.be
Beste klant,
We hebben uw inschrijving goed ontvangen en danken u voor uw vertrouwen.
Vanaf nu zorgen we voor alles, daarbij hoort ook de beëindiging van uw contract bij uw huidige leverancier.
U ontvangt een e-mail van onze klantendienst binnen de 5 werkdagen. Let op, vergeet niet om uw « junk mail » of « spam » te controleren.
Steeds tot uw dienst
Onze medewerkers zijn te uwer beschikking om uw vragen te beantwoorden. Als u nog geen klantennummer heeft, houd dan uw registratienummer WEG-17178 bij de hand.
Met energieke groeten
Het OCTA+; team
Contactgegevens
Ik ben
Particulier
Titel
Mevrouw
Naam
Van Maele
Voornaam
Céline
Tel
0478/60.64.78
E-mail vanmaeleceline@gmail.com
2. Aanvullende gegevens
Nieuwsbrief
Nee
Acties, promoties, marketing
Nee
Product elektriciteit
Care
Metertype
Tweevoudig
EAN (elektriciteit)
541448820050716492
Product Aardgas
Care
EAN (Aardgas)
541448820050716508
Facturatiemethode
Overschrijving
Frequentie
Maandelijks
U hebt onze privacy voorwaarden, die beschikbaar zijn op
https://www.yourprivacy.be/nl/octaplus geaccepteerd.
3. Leveringsadres
Postcode
8200
Gemeente
SINT-MICHIELS
Straat
Domeindreef
Nummer
7
4. Eventuele opmerkingen
© OCTA+; 2022 |
PRIVACY POLICY
Schaarbeeklei, 600
1800 Vilvoorde
T. : 02 851 01 51
E-mail : energie@octaplus.be
        """
    em=EmailMessage().read(text)
    print(em.detect_language())
    print([e.body for e in em.fragments])







