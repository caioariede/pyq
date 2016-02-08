import regex

from collections import namedtuple


Attr = namedtuple('Attr', 'lft op rgt')
Pseudo = namedtuple('Pseudo', 'name value')


class RE(object):
    id = r'_?[A-Za-z0-9_]+|_'
    ws = r'[\x20\t\r\n\f]*'
    comma = '^{ws},{ws}'.format(ws=ws)
    combinator = r'^{ws}([>+~ ]){ws}'.format(ws=ws)

    type_selector = '({id})'.format(id=id)
    id_selector = '#({id})'.format(id=id)
    class_selector = r'\.(' + id + ')'
    pseudo_selector = r'(:({id})\(([^()]+|(?1)?)\))'.format(id=id)
    attr_selector = r'\[{ws}({id}){ws}([*^$|!~]?=)(.*?)\]'.format(id=id, ws=ws)

    selector = '(?:(?:{typ})?({id}|{cls}|{pseudo}|{attr})+|{typ})'.format(
        typ=id, id=id_selector, cls=class_selector, pseudo=pseudo_selector,
        attr=attr_selector)


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

        selector_patterns = {
            'types': RE.type_selector,
            'ids': RE.id_selector,
            'classes': RE.class_selector,
            'pseudos': RE.pseudo_selector,
            'attrs': RE.attr_selector,
        }

        matches = {}

        while True:
            pattern_matched = False
            for key, pattern in selector_patterns.items():
                match = regex.search(r'^{}'.format(pattern), name)
                if match:
                    i, pos = match.span()
                    if key not in matches:
                        matches[key] = []
                    matches[key].append(match.groups())
                    name = name[pos:]
                    pattern_matched = True
            if not pattern_matched:
                break

        self.typ = None
        for types in matches.pop('types', []):
            self.typ = types[0]

        self.id_ = None
        for ids in matches.pop('ids', []):
            self.id_ = ids[0]

        self.classes = [a[0] for a in matches.pop('classes', [])]

        self.attrs = [
            Attr(l, o, r.strip())
            for l, o, r in matches.pop('attrs', [])
        ]
        self.pseudos = [
            Pseudo(*a[1:])
            for a in matches.pop('pseudos', [])
        ]

    def __repr__(self):
        return 'Selector <{}>'.format(self.name)

    @staticmethod
    def parse(string):
        selectors = []

        combinator = None
        prev_selector = None

        while True:
            match = regex.search(RE.comma, string)
            if match:
                # skip comma
                _, pos = match.span()
                string = string[pos:]
                continue

            match = regex.search(RE.combinator, string)
            if match:
                _, pos = match.span()
                combinator = string[:pos].strip()
                string = string[pos:]
            else:
                combinator = None

            match = regex.search(RE.selector, string)
            if match:
                _, pos = match.span()
                seltext = string[:pos]
                string = string[pos:]
                selector = Selector(seltext, combinator=combinator)
                if combinator is not None and prev_selector:
                    prev_selector.next_selector = prev_selector = selector
                else:
                    prev_selector = selector
                    selectors.append(selector)
                continue

            break

        return selectors
