import pandas as pd
import regex as re
from kdmt.text import clean_text

def fix_formating(text):
    text=str(text)
    text = text.replace(u'\\xa333', u' ')
    text = text.replace(u'\\u2019', u'\'')
    text = text.replace("\r\n\t\t", "")
    text = text.replace(u' B7; ', '')
    text = text.replace(u'\\xb4', u'\'')
    text = text.replace("&#43;", "+")
    text = text.replace(u'\\xa0', u' ')
    text = text.replace(u'\\xa0', u' ')
    text = text.replace(u'f\\xfcr', u'\'s')
    text = text.replace(u'\\xa', u' x')
#    text = text.replace(u"_x000D_\n_x000D_", '')
    text = text.replace(u'_x000D_', u'')
    text = text.replace(u'x000D', u'\n')
    text = text.replace(u'.à', u' a')
    text = text.replace(u' ', u'')
    text = text.replace(u'‎', u'')
    text = text.replace(u'­', '')
    text = text.replace(u'﻿', u'')
    text = text.replace('&nbsp;', u'')
    text = text.replace('&#43;', '')
    text = text.replace('&lt;', '<')
    text = text.replace('&quot;', '"')
    text = text.replace('&gt;', '>')
    text = text.replace('ï»¿', '')
    text = text.replace('...', '.')
    text = text.replace('..', '.')
    text = text.replace(' .', '. ')
    text = text.replace('\r\n', '\n')
    text = text.replace('\xa0', ' ').replace('：', ': ').replace('\u200b', '').replace('\u2026', '...').replace('’', "'")
    text = text.replace('...', '.')
    text = text.replace('..', '.')
    text = re.sub(r':\s+', ': ', text)
    #    text = text.replace('\\r', '. ')
    text = text.replace(' .', '. ')
    text = re.sub(r':\s?\.', ':', text)

    return text.strip('\n').strip().strip('\n')


def clean(text, remove_html=True, email_forward=True):
    text=str(text)
    if remove_html:
        text = re.sub(r"(<|\[)https?:\/\/.*(\.).*(>|\])", "", text, 0, re.M)
        text = re.sub(r"(?:[^\r\n\t\f\v]*{[^{}]*})+", '', text,0, re.MULTILINE)
        text = re.sub(r"(?:[^\r\n\t\f\v]*{[^{}]*})+", '', text, 0, re.MULTILINE)
        text = re.sub(r"[^\r\n\t\f\v]*\s*(\}|\{)\s*|@import.*", "", text, 0, re.MULTILINE)
        text = re.sub(r"\/\*[^*]*\*+([^/*][^*]*\*+)*\/", "", text, 0, re.MULTILINE)
    text= fix_formating(text).strip()
    text=re.sub(r"^(\s*\|\s+)+", "", text)
    text=re.sub(r"\[cid:.*\]", "", text, 0, re.MULTILINE)

    if email_forward:
        text = re.sub(r"^>+[ ]*", "", text, 0, re.MULTILINE)
    return text

def fix_email_formatting(text):

    text=re.sub(r'((?:a\s+écrit|schreef|wrote|geschreven)\s*:\s*)(>?\s*\w+)', r"\g<1>\n\g<2>",  text)
    text=re.sub(r"(\w+)(-*\s*(Message original|Original Message|Forwarded Message|Oorspronkelijk bericht|Doorgestuurd bericht|Message d'origine|Message transféré|Message transmis|Origineel bericht|Ursprüngliche Nachricht)\s*-*)(\w+)", r"\g<1>\n\g<2>\n\g<3>", text)
    text=re.sub(r"a\sécrit", "a écrit", text)
    text = re.sub(r"(\w+,?)\s+(\w+@)", r"\g<1> \g<2>",  text)
    text = re.sub(r"(Le)(lun|mar|mer|jeu|ven|sam|dim)", r"\g<1> \g<2>",  text)

    return text

if __name__ == '__main__':
    text="""Verzonden vanaf mijn Huawei mobiele telefoon
-------- Oorspronkelijk bericht --------
Van: energie@octaplus.be
Datum: ma 20 jun. 2022 09:45
Aan: els.vaes_1@hotmail.com
Onderwerp: RE: Vaes Els
Beste heer Vaes,
Hartelijk dank voor uw aanvraag.
Behoudens vergissing van onze kant, hebben wij geen bijlage mogen ontvangen.
Stuur ons gerust uw eindfactuur van de vorige leverancier. Vooral de pagina waar uw meterstanden en verbruik op genoteert staan, zijn
 belangrijk voor een herberekening van uw voorschot.
Heeft u nog vragen, reageer dan gerust op dit bericht. Mijn collega's en ikzelf helpen u graag verder.
Met energieke groeten,
Shana V.
Om al onze contactmogelijkheden, veelgestelde vragen en uw persoonlijke klantenzone te ontdekken,
klikhier.
From: Els vaes [els.vaes_1@hotmail.com]
Sent: 17/06/2022 08:33:09
To: OCTA+; Energie [energie@octaplus.be]
Subject: Vaes Els
Hierbij mijn afrekening van engie.
Ik betaal bij jullie nu meer per maand als er voor.
Mijn klantennr is 185373
Dit was niet de afspraak.
Groeten Els
Verzonden vanaf mijn Huawei mobiele telefoon
"""

    print(fix_email_formatting(text))
#    df=pd.read_excel("/Users/mohamedmentis/Dropbox/Mac (2)/Documents/Mentis/Development/Python/kolibri-ml/examples/email_data.xlsx")
#    df['body_clean']=df['body'].apply(clean)

#    df.to_excel("email_data_clean.xlsx")

