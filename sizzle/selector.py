import regex

from collections import namedtuple


Attr = namedtuple('Attr', 'lft op rgt')
Pseudo = namedtuple('Pseudo', 'name value')


class RE(object):
    id = r'_?[A-Za-z0-9_]+|_'
    ws = r'[\x20\t\r\n\f]*'
    comma = '^{ws},{ws}'.format(ws=ws)
    combinator = r'^{ws}([>+~ ]){ws}'.format(ws=ws)

    type_selector = '^{id}'.format(id=id)
    id_selector = '#({id})'.format(id=id)
    class_selector = r'\.(' + id + ')'
    pseudo_selector = r':({id})\(([^()]+|(?R)?)\)'.format(id=id)
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

        self.classes = regex.findall(RE.class_selector, name)

        self.pseudos = [
            Pseudo(*a)
            for a in regex.findall(RE.pseudo_selector, name)
        ]

        self.attrs = [
            Attr(l, o, r.strip())
            for l, o, r in regex.findall(RE.attr_selector, name)
        ]

        for typ in regex.findall(RE.type_selector, name, 1):
            self.typ = typ
            break
        else:
            self.typ = None

        for id_ in regex.findall(RE.id_selector, name, 1):
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
