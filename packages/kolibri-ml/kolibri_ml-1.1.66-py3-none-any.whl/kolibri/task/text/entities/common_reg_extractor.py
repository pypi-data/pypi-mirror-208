from kolibri.tools.regexes import Regex
from kolibri.data import load


from kolibri.tools.scanner import Scanner
from kolibri.core.entity import Entity
from kolibri.tools import regexes

class CommonRegexExtractor(Scanner):
    """ Simple JavaScript tokenizer using the Scanner class"""


    def __init__(self):
        regexe_entities = load('packages/regexes/entities.json')

        digit_regexes=[]
        for name in regexe_entities['DIGITS']:
            r=regexes.__dict__[name]
            if isinstance(r, Regex):
                digit_regexes.append(r)
            elif isinstance(r, dict):
                for sub_reg in r.values():
                    if isinstance(sub_reg, Regex):
                        digit_regexes.append(sub_reg)

        alpha_regexes=[]
        for name in regexe_entities['ALPHA']:
            r=regexes.__dict__[name]
            if isinstance(r, Regex):
                alpha_regexes.append(r)
            elif isinstance(r, dict):
                for sub_reg in r.values():
                    if isinstance(sub_reg, Regex):
                        alpha_regexes.append(sub_reg)
        super(CommonRegexExtractor, self).__init__(digit_regexes=digit_regexes, alpha_regexes=alpha_regexes)


    def process(self, src):

        return self.scan(src)

    def get_matches(self, text):
        return self.process(text)

    def addEntity(self, tok, value, start, end):
        t = Entity(tok, value.strip(), start, end)
        t.idx = self.counter
        self.counter += 1
        self.entities.append(t)

if __name__=='__main__':
    ce=CommonRegexExtractor()
    text="""De rekening van Darren Mertens, klant 281972 te Begonialaan 32/1, 1853 Grimbergen kan worden afgesloten. De flat is verkocht.
Bijgevoegd vindt u het energieovername document. Gaz: 23344,3 m3
Indien u nog vragen heeft, mag u die stellen via mail of telefoon 0472 310 709 VAN Darren Mertens. www.dell.com"""
    ents=ce.get_matches(text)

    for e in ents:
        print(e)