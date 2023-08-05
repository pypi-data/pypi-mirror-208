try:
    import eml_parser
    eml_parser_found=True
except:
    eml_parser_found = False
    pass
import eml_parser
email_parser = eml_parser.EmlParser(include_raw_body=True)

def parse_eml(eml_file):

    with open(eml_file, 'rb') as fhdl:
        raw_email = fhdl.read()



    parsed_eml = email_parser.decode_email_bytes(raw_email)

    in_replay =""
    if 'in-reply-to' in parsed_eml['header']['header']:
        in_replay =parsed_eml['header']['header']['in-reply-to']

    attachements =[]
    if 'attachment' in parsed_eml:
        attachements =[att['filename'] for att in parsed_eml['attachment']]
    language =""
    if 'content-language' in parsed_eml['header']['header']:
        language =parsed_eml['header']['header']['content-language'][0]
    body =""
    references =""
    if 'message-id' in parsed_eml['header']['header']:
        references = parsed_eml['header']['header']['message-id']
    if len(parsed_eml['body']) > 0:
        body =parsed_eml['body'][0]['content']

    return{
        "body": body,
        "title": parsed_eml['header']['subject'],
        "from": parsed_eml['header']['from'],
        "to": parsed_eml['header']['to'],
        "date": parsed_eml['header']['date'],
        "from_name": parsed_eml['header']['header']['from'][0],
        "language": language,
        'message-id' :references,
        "in_replay_to" :in_replay,
        "attachement_names" :attachements
    }