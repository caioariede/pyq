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


def sel(selector):
    for sel in selector.split(','):
        yield Selector.build(sel.strip())


if __name__ == '__main__':
    import unittest

    class TestSObjs(unittest.TestCase):
        def test_class_selector(self):
            sobjs = list(sel('.class > def'))

            self.assertEqual(len(sobjs), 1)
            self.assertEqual(sobjs[0].name, '.class')

        def test_class_selector_child(self):
            sobjs = list(sel('.class > def'))

            self.assertEqual(len(sobjs), 1)
            self.assertEqual(sobjs[0].name, '.class')
            self.assertIsNotNone(sobjs[0]._next)

            self.assertEqual(sobjs[0]._next.name, 'def')
            self.assertTrue(sobjs[0]._next._direct)

        def test_type_selector(self):
            sobjs = list(sel('class'))

            self.assertEqual(len(sobjs), 1)
            self.assertEqual(sobjs[0].name, 'class')

        def test_composed_selector(self):
            sobjs = list(sel('class.foo.bar'))

            self.assertEqual(len(sobjs), 1)
            self.assertIsInstance(sobjs[0], Selector)
            self.assertEqual(sobjs[0].typ, 'class')
            self.assertEqual(sobjs[0].classes, ['foo', 'bar'])

        def test_child_selector(self):
            sobjs = list(sel('class > def'))

            self.assertEqual(len(sobjs), 1)
            self.assertIsInstance(sobjs[0], Selector)
            self.assertEqual(sobjs[0].name, 'class')
            self.assertIsNotNone(sobjs[0]._next)

            self.assertEqual(sobjs[0]._next.name, 'def')
            self.assertTrue(sobjs[0]._next._direct)

        def test_nonchild_selector(self):
            sobjs = list(sel('class def'))

            self.assertEqual(len(sobjs), 1)
            self.assertEqual(sobjs[0].name, 'class')
            self.assertIsNotNone(sobjs[0]._next)

            self.assertEqual(sobjs[0]._next.name, 'def')

        def test_pseudos(self):
            sobjs = list(sel(':not(1)'))

            self.assertEqual(len(sobjs), 1)
            self.assertEqual(len(sobjs[0].pseudos), 1)
            self.assertEqual(sobjs[0].pseudos[0][0], 'not')
            self.assertEqual(sobjs[0].pseudos[0][1], '1')

        def test_nested_pseudos(self):
            sobjs = list(sel(':not(:not(1))'))

            self.assertEqual(len(sobjs), 1)
            self.assertEqual(len(sobjs[0].pseudos), 1)
            self.assertEqual(sobjs[0].pseudos[0][0], 'not')
            self.assertEqual(sobjs[0].pseudos[0][1], ':not(1)')

        def test_compound_pseudos(self):
            sobjs = list(sel(':not(1):not(2)'))

            self.assertEqual(len(sobjs), 1)
            self.assertEqual(len(sobjs[0].pseudos), 2)
            self.assertEqual(sobjs[0].pseudos[0][0], 'not')
            self.assertEqual(sobjs[0].pseudos[0][1], '1')
            self.assertEqual(sobjs[0].pseudos[1][0], 'not')
            self.assertEqual(sobjs[0].pseudos[1][1], '2')

    # test custom matcher
    from collections import namedtuple

    class TestCustomMatcher(unittest.TestCase):
        CLS = namedtuple('ClassDef', ('name', 'extends', 'body'))
        DEF = namedtuple('FunctionDef', ('name',))

        def match(self, selector, data):
            sobjs = list(sel(selector))
            result = list(self._match(sobjs, data))
            return result

        def _match(self, sobjs, data):
            for sobj in sobjs:
                yield from self._match_sub(sobj, data)

        def _match_sub(self, sobj, data):
            for d in data:
                match = self._match_rules(sobj, d)

                if match:
                    if sobj._next:
                        if hasattr(d, 'body'):
                            yield from self._match_sub(sobj._next, d.body)
                    else:
                        yield d

                if hasattr(d, 'body') and not sobj._direct:
                    yield from self._match_sub(sobj, d.body)

        def _match_rules(self, sobj, d):
            match = all(self._match_item(sobj, d))

            if match and sobj.pseudos:
                match &= all(self._match_pseudos(sobj, d))

            return match

        def _match_item(self, sobj, d):
            if sobj.typ:
                typcls = {
                    'class': self.CLS,
                    'def': self.DEF,
                }

                yield isinstance(d, typcls[sobj.typ])

            if sobj.id_:
                yield d.name == sobj.id_

        def _match_pseudos(self, sobj, d):
            for p in sobj.pseudos:
                if p[0] == 'not':
                    yield not self._match_rules(Selector.build(p[1]), d)
                elif p[0] == 'extends':
                    yield p[1] in getattr(d, 'extends', [])

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

        def test_typ(self):
            self.assertEqual(len(self.match('class', self.data)), 2)
            self.assertEqual(len(self.match('class, def', self.data)), 6)

        def test_child(self):
            self.assertEqual(len(self.match('class > def', self.data)), 3)

        def test_ids(self):
            self.assertEqual(len(self.match('def#bla', self.data)), 0)
            self.assertEqual(len(self.match('def#foo', self.data)), 1)

        def test_pseudos(self):
            return
            self.assertEqual(len(self.match(':extends(object)', self.data)), 1)

        def test_nested_pseudos(self):
            self.assertEqual(
                len(self.match(':not(:extends(object))', self.data)), 5)
            self.assertEqual(
                len(self.match(':extends(object):not(def)', self.data)), 1)
            self.assertEqual(
                len(self.match(':not(def)', self.data)), 2)

    unittest.main()
