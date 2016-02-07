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


class MatchEngine(object):
    pseudo_fns = {}

    def __init__(self):
        self.register_pseudo('not', self.pseudo_not)

    def register_pseudo(self, name, fn):
        self.pseudo_fns[name] = fn

    @staticmethod
    def pseudo_not(matcher, node, value):
        return not matcher.match_node(Selector.build(value), node)

    def match(self, selector, data):
        selectors = Selector.parse(selector)
        for selector in selectors:
            yield from self.match_data(selector, data)

    def match_data(self, selector, data):
        for node, body in self._iter_data(data):
            match = self.match_node(selector, node)

            if match:
                if selector._next:
                    if body:
                        yield from self.match_data(selector._next, body)
                else:
                    yield node

            if body and not selector._direct:
                yield from self.match_data(selector, body)

    def match_node(self, selector, node):
        match = all(self.match_rules(selector, node))

        if match and selector.pseudos:
            match &= all(self.match_pseudos(selector, node))

        return match

    def match_rules(self, selector, node):
        if selector.typ:
            yield self.match_type(selector.typ, node)

        if selector.id_:
            yield self.match_id(selector.id_, node)

    def match_pseudos(self, sobj, d):
        for p in sobj.pseudos:
            yield self.pseudo_fns[p[0]](self, d, p[1])

    def _iter_data(self, data):
        for tupl in self.iter_data(data):
            if len(tupl) != 2:
                raise Exception(
                    'The iter_data method must yield pair tuples containing '
                    'the node and its body (empty if not available)')
            yield tupl

    def match_type(self, typ, node):
        raise NotImplementedError

    def match_id(self, id_, node):
        raise NotImplementedError

    def iter_data(self, data):
        raise NotImplementedError


class CustomMatchEngine(MatchEngine):
    def __init__(self):
        super().__init__()
        self.register_pseudo('extends', self.pseudo_extends)

    @staticmethod
    def pseudo_extends(matcher, node, value):
        return value in getattr(node, 'extends', [])

    def match_type(self, typ, node):
        if typ == 'class':
            cls = self.CLS
        elif typ == 'def':
            cls = self.DEF

        return isinstance(node, cls)

    def match_id(self, id_, node):
        return node.name == id_

    def iter_data(self, data):
        for node in data:
            yield node, getattr(node, 'body', None)


if __name__ == '__main__':
    import unittest

    class TestSObjs(unittest.TestCase):
        def test_class_selector(self):
            sobjs = list(Selector.parse('.class > def'))

            self.assertEqual(len(sobjs), 1)
            self.assertEqual(sobjs[0].name, '.class')

        def test_class_selector_child(self):
            sobjs = list(Selector.parse('.class > def'))

            self.assertEqual(len(sobjs), 1)
            self.assertEqual(sobjs[0].name, '.class')
            self.assertIsNotNone(sobjs[0]._next)

            self.assertEqual(sobjs[0]._next.name, 'def')
            self.assertTrue(sobjs[0]._next._direct)

        def test_type_selector(self):
            sobjs = list(Selector.parse('class'))

            self.assertEqual(len(sobjs), 1)
            self.assertEqual(sobjs[0].name, 'class')

        def test_composed_selector(self):
            sobjs = list(Selector.parse('class.foo.bar'))

            self.assertEqual(len(sobjs), 1)
            self.assertIsInstance(sobjs[0], Selector)
            self.assertEqual(sobjs[0].typ, 'class')
            self.assertEqual(sobjs[0].classes, ['foo', 'bar'])

        def test_child_selector(self):
            sobjs = list(Selector.parse('class > def'))

            self.assertEqual(len(sobjs), 1)
            self.assertIsInstance(sobjs[0], Selector)
            self.assertEqual(sobjs[0].name, 'class')
            self.assertIsNotNone(sobjs[0]._next)

            self.assertEqual(sobjs[0]._next.name, 'def')
            self.assertTrue(sobjs[0]._next._direct)

        def test_nonchild_selector(self):
            sobjs = list(Selector.parse('class def'))

            self.assertEqual(len(sobjs), 1)
            self.assertEqual(sobjs[0].name, 'class')
            self.assertIsNotNone(sobjs[0]._next)

            self.assertEqual(sobjs[0]._next.name, 'def')

        def test_pseudos(self):
            sobjs = list(Selector.parse(':not(1)'))

            self.assertEqual(len(sobjs), 1)
            self.assertEqual(len(sobjs[0].pseudos), 1)
            self.assertEqual(sobjs[0].pseudos[0][0], 'not')
            self.assertEqual(sobjs[0].pseudos[0][1], '1')

        def test_nested_pseudos(self):
            sobjs = list(Selector.parse(':not(:not(1))'))

            self.assertEqual(len(sobjs), 1)
            self.assertEqual(len(sobjs[0].pseudos), 1)
            self.assertEqual(sobjs[0].pseudos[0][0], 'not')
            self.assertEqual(sobjs[0].pseudos[0][1], ':not(1)')

        def test_compound_pseudos(self):
            sobjs = list(Selector.parse(':not(1):not(2)'))

            self.assertEqual(len(sobjs), 1)
            self.assertEqual(len(sobjs[0].pseudos), 2)
            self.assertEqual(sobjs[0].pseudos[0][0], 'not')
            self.assertEqual(sobjs[0].pseudos[0][1], '1')
            self.assertEqual(sobjs[0].pseudos[1][0], 'not')
            self.assertEqual(sobjs[0].pseudos[1][1], '2')

    # test custom matcher
    class TestCustomMatcher(unittest.TestCase):
        from collections import namedtuple

        CLS = namedtuple('ClassDef', ('name', 'extends', 'body'))
        DEF = namedtuple('FunctionDef', ('name',))

        def setUp(self):
            self.data = [
                self.CLS('Test', ['object'], [
                    self.DEF('foo'),
                    self.DEF('bar'),
                    self.CLS('Test2', [], [
                        self.DEF('baz'),
                    ])
                ]),
                self.DEF('baz'),
            ]

            self.matcher = CustomMatchEngine()
            self.matcher.CLS = self.CLS
            self.matcher.DEF = self.DEF

            self.match = lambda s: list(self.matcher.match(s, self.data))

        def test_typ(self):
            self.assertEqual(len(self.match('class')), 2)
            self.assertEqual(len(self.match('class, def')), 6)

        def test_child(self):
            self.assertEqual(len(self.match('class > def')), 3)

        def test_ids(self):
            self.assertEqual(len(self.match('def#bla')), 0)
            self.assertEqual(len(self.match('def#foo')), 1)

        def test_pseudos(self):
            self.assertEqual(len(self.match(':extends(object)')), 1)

        def test_nested_pseudos(self):
            self.assertEqual(
                len(self.match(':not(:extends(object))')), 5)
            self.assertEqual(
                len(self.match(':extends(object):not(def)')), 1)
            self.assertEqual(
                len(self.match(':not(def)')), 2)

    unittest.main()
