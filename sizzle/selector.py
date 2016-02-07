import regex

from collections import namedtuple


ID = r'_?[A-Za-z0-9_]+|_'
WS = r'[\x20\t\r\n\f]*'

COMMARE = '^{ws},{ws}'.format(ws=WS)
TYPRE = '^{id}'.format(id=ID)
IDRE = '#({id})'.format(id=ID)
CLSRE = r'\.(' + ID + ')'
PSEUDORE = r':({id})\(([^()]+|(?R)+)\)'.format(id=ID)
ATTRRE = r'\[{ws}({id}){ws}([*^$|!~]?=)(.*)\]'.format(id=ID, ws=WS)
COMBINATOR = r'^{ws}([>+~ ]){ws}'.format(ws=WS)
SELECTOR = '(?:(?:{typ})?({id}|{cls}|{pseudo}|{attr})+|{typ})'.format(
    typ=ID, id=IDRE, cls=CLSRE, pseudo=PSEUDORE, attr=ATTRRE)


Attr = namedtuple('Attr', 'lft op rgt')
Pseudo = namedtuple('Pseudo', 'name value')


class Selector(object):
    DESCENDANT = ' '
    CHILD = '>'
    SIBLING = '~'
    ADJACENT = '+'
    NOT_SET = None

    def __init__(self, name, combinator=None):
        self.name = name
        self.combinator = combinator
        self.next_selector = None

        self.classes = regex.findall(CLSRE, name)
        self.pseudos = [Pseudo(*a) for a in regex.findall(PSEUDORE, name)]
        self.attrs = [Attr(*a) for a in regex.findall(ATTRRE, name)]

        for typ in regex.findall(TYPRE, name, 1):
            self.typ = typ
            break
        else:
            self.typ = None

        for id_ in regex.findall(IDRE, name, 1):
            self.id_ = id_
            break
        else:
            self.id_ = None

    def __repr__(self):
        return 'Selector <{}>'.format(self.name)

    @staticmethod
    def parse(string):
        selectors = []

        combinator = None

        ref = {'prev': None}

        while True:
            match = regex.search(COMMARE, string)
            if match:
                # skip comma
                _, pos = match.span()
                string = string[pos:]
                continue

            match = regex.search(COMBINATOR, string)
            if match:
                _, pos = match.span()
                combinator = string[:pos].strip()
                string = string[pos:]
            else:
                combinator = None

            match = regex.search(SELECTOR, string)
            if match:
                _, pos = match.span()
                seltext = string[:pos]
                string = string[pos:]
                selector = Selector(seltext, combinator=combinator)
                if combinator is not None and ref['prev']:
                    ref['prev'].next_selector = ref['prev'] = selector
                else:
                    ref['prev'] = selector
                    selectors.append(selector)
                continue

            break

        return selectors

    @classmethod
    def build_sub(cls, sub, sep=None, _next=None, _direct=False):
        if _next is not None:
            _next = cls.build(_next, _direct=sep is not None)

        typ = regex.findall(TYPRE, sub)
        id_ = regex.findall(IDRE, sub)
        classes = regex.findall(CLSRE, sub)
        pseudos = regex.findall(PSEUDORE, sub)
        attrs = regex.findall(ATTRRE, sub)

        if typ:
            typ = typ[0]

        if id_:
            id_ = id_[0]

        return cls(sub, typ=typ, id_=id_, classes=classes, pseudos=pseudos,
                   attrs=attrs, _next=_next, _direct=_direct)
