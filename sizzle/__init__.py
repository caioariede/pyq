from selector import Selector
from match import MatchEngine


__all__ = ('Selector', 'MatchEngine')


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
