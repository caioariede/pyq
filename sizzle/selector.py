import regex


ID = r'_?[A-Za-z0-9_]*'

SUBSEL_RE = r'\s*(>)\s*|\s+'
TYPRE = '^{id}'.format(id=ID)
IDRE = '#({id})'.format(id=ID)
CLSRE = r'\.(' + ID + ')'
PSEUDORE = r':({id})\(([^()]+|(?R)+)\)'.format(id=ID)


class Selector(object):
    def __init__(self, name, id_=None, typ=None, classes=None, pseudos=None,
                 _next=None, _direct=False):
        self.name = name
        self.typ = typ
        self.id_ = id_
        self.classes = classes or []
        self.pseudos = pseudos or []
        self._next = _next
        self._direct = _direct

    def __repr__(self):
        return 'Selector <{}>'.format(self.name)

    @staticmethod
    def parse(string):
        for sel in string.split(','):
            yield Selector.build(sel.strip())

    @classmethod
    def build(cls, sel, _direct=False):
        subs = regex.split(SUBSEL_RE, sel, 1)

        if len(subs) == 1:
            return cls.build_sub(subs[0], _direct=_direct)

        sub, sep, nxt = subs

        return cls.build_sub(sub, sep=sep, _next=nxt, _direct=_direct)

    @classmethod
    def build_sub(cls, sub, sep=None, _next=None, _direct=False):
        if _next is not None:
            _next = cls.build(_next, _direct=sep is not None)

        typ = regex.findall(TYPRE, sub)
        id_ = regex.findall(IDRE, sub)
        classes = regex.findall(CLSRE, sub)
        pseudos = regex.findall(PSEUDORE, sub)

        if typ:
            typ = typ[0]

        if id_:
            id_ = id_[0]

        return cls(sub, typ=typ, id_=id_, classes=classes, pseudos=pseudos,
                   _next=_next, _direct=_direct)
