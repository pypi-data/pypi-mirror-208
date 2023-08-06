from pathlib import Path
from kolibri.data import load

patterns_file=load('packages/tokenizers/default_regexes.json')


functions =load('packages/gazetteers/default/Job_Functions.txt', as_array=True)
disclaimers =load('packages/gazetteers/default/disclaimers.txt', as_array=True)
salutation_opening_statements =load('packages/gazetteers/default/salutations.txt', as_array=True)
salutation_opening_strict =load('packages/gazetteers/default/salutations_strict.txt', as_array=True)
email_closings =load('packages/gazetteers/default/email_closing.txt', as_array=True)
rejected_emails_formulas=load('packages/gazetteers/default/rejected_email.txt', as_array=True)
ooo_emails_formulas=load('packages/gazetteers/default/out_of_office.txt', as_array=True)
sent_from_my_device=load('packages/gazetteers/default/sent_from_my_device.txt', as_array=True)
email_caution_or_fron_content=load('packages/gazetteers/default/email_caution_or_front_content.txt', as_array=True)

language = 'en'

disclaimer_openings = [d.strip() for d in disclaimers if d.strip()]
pattern_disclaimer = r"[\s*]*(?P<disclaimer_text>(" + "|".join(disclaimer_openings) + ")(\s*\w*))"



pattern_salutation = r'(?P<salutation>(^[>|\s-]*\b((' + r'|'.join(
    salutation_opening_statements) + r'))\b)[ ]*(,|\.)?)'

pattern_salutation_colated = r'(?P<salutation>([>|\s-]*\b((' + r'|'.join(
    salutation_opening_strict) + r'))\b)[ ]*(,|\.)?)'



signature_pattern = r'(^[|\.\s>]?)(?P<signature>\s*\b(' + r'|'.join(email_closings) + r')(,|.)?\s*)'

signature_pattern_colated_text = r'([|\.\s>]?)\s*(?P<signature>\b(' + r'|'.join(email_closings) + r')(,|.)?\s*)'

signature_pattern = r'(?P<signature>(^[|\.\s>]?)\s*\b(' + r'|'.join(email_closings) + r')(,|.)?\s*)'
signature_pattern_bis = r'(?P<signature>^\s*\b(' + r'|'.join(email_closings) + r')(,|.)?\s*)'


function_re = ''
for funct in functions:
    function_re += funct.strip('\n') + '|'

function_re = function_re[:-1]

function_re = r'(?P<signature>(([A-Z][a-z]+\s?)+)?(\s?[\|,]\s?)?({})(.+)?)'.format(function_re)

catch_all = r"[0-9A-Za-z一-龠ぁ-ゔァ-ヴー ÑÓżÉÇÃÁªçã$łÄÅäýñëàźiîåüöóąèûìíśćłńé«»°êùáÀèôú⺀-⺙⺛-⻳⼀-⿕々〇〡-〩〸-〺〻㐀-䶵一-鿃豈-鶴侮-頻並-龎 \/@\.:,;\&\?\(\)'´s_\"\*[\]\%+<>#\/\+\s\t_=-]+"
catch_all_oneLine = catch_all.replace('\s', '')[:-1]
catch_all_oneLine = catch_all_oneLine[:1] + '\|' + catch_all_oneLine[1:]


# regex_headers = [
#
#     r"((From|To|De|Da|V[ao]n|发件人|Från|Fra|Expéditeur)\s*:" + catch_all + "?(((Subject|Objet|Oggetto|Asunto|Onderwerp|Betreff|主题|Ämne|Ass?unto|Tema)\s*:\s?)(?P<subject>(" + catch_all_oneLine + ")+))|((Sent\sat|Enviado\sa|Enviada à\(s\)|Datum|Date|Envoyé|Verzonden|Sent)\s*:" + catch_all_oneLine + "))",
#     r"On\s+(\d{2}|Mon(day)?|Tue(sday)?|Wed(nesday)?|Thu(rsday)?|Friday|Sat(urday)?|Sun(day)?)" + catch_all + "(wrote):",
#     r"\s{0, 10}(\d{1,2})?\s?(Jan|Feb|Mar|Apr|Mai|Jun|Jul|Aug|Sep|Nov|Oct|Dec)\s?(\d{1,2})?,\s+\d{2}:\d{2}\s+UTC$",
#     r"(Op|Le|On)\s.*\s(om|à|\?|at|\d{2}:\d{2})\s*.*\s?.*(schreef|a (é|\?)crit|wrote|geschreven)\s*(:)?",
#     r"(\d{2}|Mon(day)?|Tue(sday)?|Wed(nesday)?|Thu(rsday)?|Friday|Sat(urday)?|Sun(day)?).*(mailto:.*$)",
#     r"(Op|Le|On)\s+(?P<date>([0-9A-Za-z一-龠ぁ-ゔァ-ヴー ÑÓżÉÇÃÁªçã$łÄÅäýñëàźiîåüöóąèûìíśćłńé«»°êùáÀèôú⺀-⺙⺛-⻳⼀-⿕々〇〡-〩〸-〺〻㐀-䶵一-鿃豈-鶴侮-頻並-龎 \/@\.:,;\&\?\(\)'´s_\"\*[\]\%+<>#\/\+\s\t_=-]+))\b(om|at|schreef|wrote|a écrit|geschreven)\b(.*)?\s*:"
# ]
regex_headers = [
    r"((From|De|Da|V[ao]n|发件人|Från|Fra|Expéditeur)\s*:.*)|^\b(Op|Le|On)\b.*[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}",
    r"^\b(Op|Le|On)\b\s.*\s(om|à|at|\d{2}:\d{2})\s*.*(schreef|a écrit|wrote|geschreven)\s*(:)?"
]

header_date_regex= '|'.join([r"(Sent\sat|Enviado(\s(a|el))?|Enviada à\(s\)|Gesendet|Verzonden|Envoyés|Datum|Date|Data|Fecha|Inviato|Envoyé(\s+le)?|Verzonden|Verstuurd|Sent)\s*:\s*(?P<date>(.*$))",
                   r"The original message was received at\s*(?P<date>(.*))|(Op|Le|On)\s+(?P<date>(.*))\b(om|at|schreef|wrote|a écrit|geschreven)\b(.*)?\s*:",
                    r"(Op|Le|On)\b(?P<date>.*[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})|(Op|Le|On)(?P<date>\s.*\s(om|à|at|\d{2}:\d{2})\s*.*)(schreef|a écrit|wrote|geschreven)\s*(:)?",
                             "-*\s*(Message original|Original Message|Origineel bericht|Forwarded Message|Ursprüngliche Nachricht|Oorspronkelijk bericht|Doorgestuurd bericht|Message d'origine|Message transféré|Message transmis)\s*-*"
                             ])
header_from_regex= r"(((F|f)rom|De|Da|V[ao]n|发件人|Från|Fra|Expéditeur)\s*:.*[<\[ ]((?P<from>[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})))|((schreef|wrote|a écrit)\s(?P<from>[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b))|(mailto:|heeft\s)(?P<from>[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})|((?P<from>[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b)(.*)(schreef|wrote|a écrit)\s)"
header_subject_regex=r"(((Subject|Sujet|Objet|Oggetto|Asunto|Onderwerp|Betreff|主题|Ämne|Ass?unto|Tema)\s*:\s?)(?P<subject>(.*)+))"
header_to_regex=r"(((To|Aan|À|Destinataire)\s*:\s?)(?P<to>(.*)+))"
header_cc_regex=r"C(C|c)\s*:\s*.*$"