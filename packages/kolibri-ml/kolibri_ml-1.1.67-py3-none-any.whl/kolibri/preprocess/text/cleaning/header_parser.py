from kolibri.preprocess.text.cleaning.__email_configs import header_from_regex, header_subject_regex, header_date_regex, header_to_regex, header_cc_regex
import regex as re
from kdmt.dateparser import find_dates
class HeaderParser():
    def __init__(self, parse_dates=False):
        self.fromRE=re.compile(header_from_regex)
        self.subjectRE=re.compile(header_subject_regex)
        self.dateRE=re.compile(header_date_regex)
        self.toRE=re.compile(header_to_regex)
        self.ccRE=re.compile(header_cc_regex)
        self.parse_dates=parse_dates

    def parse(self, email):
        nb_headers_lines=6
        email=re.sub(r"^>\s*+", "", email, 0, re.MULTILINE)
        lines=email.split('\n')

        body=[]
        header_dict={}
        i=0
#        print('--------------------------------')
        for line in lines:
            if line.strip() !="":
                i=i+1
            if i<nb_headers_lines and self.ccRE.search(line):
                continue
            elif i<nb_headers_lines and self.fromRE.search(line) and 'From' not in header_dict:
     ##           i+=1
                from_=re.search(self.fromRE, line)
                from_text = from_.groupdict()["from"]
                header_dict['From']= from_text

                if self.parse_dates and i < nb_headers_lines and self.dateRE.search(line):
                    #                i+=1
                    date = re.search(self.dateRE, line)
                    date_text = date.groupdict()["date"]
                    matches = find_dates(date_text, source=True)
                    if matches is not None:
                        for m in matches:
                            date, date_text = m
                            break
                    else:
                        print(date_text)
                        print(line)
                    header_dict['Date'] = date_text
                    header_dict['Date_parsed'] = date
            elif i<nb_headers_lines and self.subjectRE.search(line):
     #           i+=1
                subject=re.search(self.subjectRE, line)
                subject_text = subject.groupdict()["subject"]
                header_dict['Subject']= subject_text
            elif i<nb_headers_lines and self.dateRE.search(line):
#                i+=1
                date =re.search(self.dateRE, line)
                date_text = date.groupdict()["date"]
                if date_text is None:
                    continue
                matches = find_dates(date_text, source=True)
                if matches is not None:
                    for m in matches:
                        date, date_text=m
                        break
                else:
                    print(date_text)
                    print(line)
                header_dict['Date']= date_text
                header_dict['Date_parsed']=date
                if isinstance(date, re.Match):
                    print(date_text)
            elif i<nb_headers_lines and self.toRE.search(line):
#                i+=1
                to=re.search(self.toRE, line)
                to_text = to.groupdict()["to"]
                header_dict['To']= to_text
            else:
                body.append(line)
        self.body='\n'.join(body)
        return header_dict