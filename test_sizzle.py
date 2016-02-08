from sizzle.selector import Selector
from sizzle.match import MatchEngine

import unittest


class TestSObjs(unittest.TestCase):
    def test_type_selector(self):
        sobjs = Selector.parse('class')

        self.assertEqual(len(sobjs), 1)
        self.assertEqual(sobjs[0].name, 'class')

    def test_multiple_selectors(self):
        sobjs = Selector.parse('class, def')

        self.assertEqual(len(sobjs), 2)
        self.assertEqual(sobjs[0].name, 'class')
        self.assertEqual(sobjs[1].name, 'def')

    def test_composed_selector(self):
        sobjs = Selector.parse('class.foo.bar')

        self.assertEqual(len(sobjs), 1)
        self.assertIsInstance(sobjs[0], Selector)
        self.assertEqual(sobjs[0].typ, 'class')
        self.assertEqual(sobjs[0].classes, ['foo', 'bar'])

    def test_class_selector(self):
        sobjs = Selector.parse('.class > def')

        self.assertEqual(len(sobjs), 1)
        self.assertEqual(sobjs[0].name, '.class')

    def test_class_selector_child(self):
        sobjs = Selector.parse('.class > def')

        self.assertEqual(len(sobjs), 1)
        self.assertEqual(sobjs[0].name, '.class')
        self.assertIsNotNone(sobjs[0].next_selector)

        self.assertEqual(sobjs[0].next_selector.name, 'def')
        self.assertEqual(sobjs[0].next_selector.combinator,
                         Selector.CHILD)

    def test_child_selector(self):
        sobjs = Selector.parse('class > def')

        self.assertEqual(len(sobjs), 1)
        self.assertIsInstance(sobjs[0], Selector)
        self.assertEqual(sobjs[0].name, 'class')
        self.assertIsNotNone(sobjs[0].next_selector)

        self.assertEqual(sobjs[0].next_selector.name, 'def')
        self.assertEqual(sobjs[0].next_selector.combinator, Selector.CHILD)

    def test_deep_selector(self):
        sobjs = Selector.parse('class > def foo > bar')

        self.assertEqual(len(sobjs), 1)
        self.assertEqual(sobjs[0].name, 'class')
        self.assertEqual(sobjs[0].next_selector.name, 'def')
        self.assertEqual(sobjs[0].next_selector.next_selector.name, 'foo')
        self.assertEqual(
            sobjs[0].next_selector.next_selector.next_selector.name, 'bar')

        self.assertEqual(sobjs[0].next_selector.name, 'def')
        self.assertEqual(sobjs[0].next_selector.combinator, Selector.CHILD)

    def test_nonchild_selector(self):
        sobjs = Selector.parse('class def')

        self.assertEqual(len(sobjs), 1)
        self.assertEqual(sobjs[0].name, 'class')
        self.assertIsNotNone(sobjs[0].next_selector)

        self.assertEqual(sobjs[0].next_selector.name, 'def')

    def test_pseudos(self):
        sobjs = Selector.parse(':not(1)')

        self.assertEqual(len(sobjs), 1)
        self.assertEqual(len(sobjs[0].pseudos), 1)
        self.assertEqual(sobjs[0].pseudos[0].name, 'not')
        self.assertEqual(sobjs[0].pseudos[0].value, '1')

    def test_pseudo_empty(self):
        sobjs = Selector.parse(':not()')

        self.assertEqual(len(sobjs), 1)
        self.assertEqual(len(sobjs[0].pseudos), 1)
        self.assertEqual(sobjs[0].pseudos[0].name, 'not')
        self.assertEqual(sobjs[0].pseudos[0].value, '')

    def test_nested_pseudos(self):
        sobjs = Selector.parse(':not(:not(1))')

        self.assertEqual(len(sobjs), 1)
        self.assertEqual(len(sobjs[0].pseudos), 1)
        self.assertEqual(sobjs[0].pseudos[0].name, 'not')
        self.assertEqual(sobjs[0].pseudos[0].value, ':not(1)')

    def test_compound_pseudos(self):
        sobjs = Selector.parse(':not(1):not(2)')

        self.assertEqual(len(sobjs), 1)
        self.assertEqual(len(sobjs[0].pseudos), 2)
        self.assertEqual(sobjs[0].pseudos[0].name, 'not')
        self.assertEqual(sobjs[0].pseudos[0].value, '1')
        self.assertEqual(sobjs[0].pseudos[1].name, 'not')
        self.assertEqual(sobjs[0].pseudos[1].value, '2')

    def test_attrs(self):
        sobjs = Selector.parse('[name=1]')

        self.assertEqual(len(sobjs), 1)
        self.assertEqual(len(sobjs[0].attrs), 1)
        self.assertEqual(sobjs[0].attrs[0].lft, 'name')
        self.assertEqual(sobjs[0].attrs[0].op, '=')
        self.assertEqual(sobjs[0].attrs[0].rgt, '1')

    def test_attrs_empty(self):
        sobjs = Selector.parse('[name!=]')

        self.assertEqual(len(sobjs), 1)
        self.assertEqual(len(sobjs[0].attrs), 1)
        self.assertEqual(sobjs[0].attrs[0].lft, 'name')
        self.assertEqual(sobjs[0].attrs[0].op, '!=')
        self.assertEqual(sobjs[0].attrs[0].rgt, '')

    def test_attrs_whitespace(self):
        sobjs = Selector.parse('[ name = 1 ]')

        self.assertEqual(len(sobjs), 1)
        self.assertEqual(len(sobjs[0].attrs), 1)
        self.assertEqual(sobjs[0].attrs[0].lft, 'name')
        self.assertEqual(sobjs[0].attrs[0].op, '=')
        self.assertEqual(sobjs[0].attrs[0].rgt, '1')

    def test_deep_attrs(self):
        sobjs = Selector.parse('[name=1] > [name=2]')

        self.assertEqual(len(sobjs), 1)
        self.assertEqual(len(sobjs[0].attrs), 1)
        self.assertEqual(sobjs[0].attrs[0].lft, 'name')
        self.assertEqual(sobjs[0].attrs[0].op, '=')
        self.assertEqual(sobjs[0].attrs[0].rgt, '1')
        self.assertEqual(sobjs[0].next_selector.attrs[0].lft, 'name')
        self.assertEqual(sobjs[0].next_selector.attrs[0].op, '=')
        self.assertEqual(sobjs[0].next_selector.attrs[0].rgt, '2')

    def test_attr_in_pseudo(self):
        sobjs = Selector.parse(':not([name=1])')

        self.assertEqual(len(sobjs), 1)
        self.assertEqual(len(sobjs[0].attrs), 0)
        self.assertEqual(len(sobjs[0].pseudos), 1)
        self.assertEqual(sobjs[0].pseudos[0].name, 'not')
        self.assertEqual(sobjs[0].pseudos[0].value, '[name=1]')


class CustomMatchEngine(MatchEngine):
    def __init__(self):
        super().__init__()
        self.register_pseudo('extends', self.pseudo_extends)

    @staticmethod
    def pseudo_extends(matcher, node, value):
        if not value:
            return hasattr(node, 'extends') and not node.extends
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

    def test_pseudos_noargs(self):
        self.assertEqual(len(self.match(':extends()')), 1)

    def test_nested_pseudos(self):
        self.assertEqual(
            len(self.match(':not(:extends(object))')), 5)
        self.assertEqual(
            len(self.match(':extends(object):not(def)')), 1)
        self.assertEqual(
            len(self.match(':not(def)')), 2)


unittest.main(failfast=True)
