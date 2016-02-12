from .selector import Selector


class MatchEngine(object):
    pseudo_fns = {}
    selector_class = Selector

    def __init__(self):
        self.register_pseudo('not', self.pseudo_not)
        self.register_pseudo('has', self.pseudo_has)

    def register_pseudo(self, name, fn):
        self.pseudo_fns[name] = fn

    @staticmethod
    def pseudo_not(matcher, node, value):
        return not matcher.match_node(matcher.parse_selector(value)[0], node)

    @staticmethod
    def pseudo_has(matcher, node, value):
        for node, body in matcher.iter_data([node]):
            if body:
                return any(
                    matcher.match_data(matcher.parse_selector(value)[0], body))

    def parse_selector(self, selector):
        return self.selector_class.parse(selector)

    def match(self, selector, data):
        selectors = self.parse_selector(selector)
        nodeids = {}
        for selector in selectors:
            for node in self.match_data(selector, data):
                nodeid = id(node)
                if nodeid not in nodeids:
                    nodeids[nodeid] = None
                    yield node

    def match_data(self, selector, data):
        for node, body in self._iter_data(data):
            match = self.match_node(selector, node)

            if match:
                next_selector = selector.next_selector
                if next_selector:
                    if body:
                        for node in self.match_data(next_selector, body):
                            yield node
                else:
                    yield node

            if body and not selector.combinator == self.selector_class.CHILD:
                for node in self.match_data(selector, body):
                    yield node

    def match_node(self, selector, node):
        match = all(self.match_rules(selector, node))

        if match and selector.attrs:
            match &= all(self.match_attrs(selector, node))

        if match and selector.pseudos:
            match &= all(self.match_pseudos(selector, node))

        return match

    def match_rules(self, selector, node):
        if selector.typ:
            yield self.match_type(selector.typ, node)

        if selector.id_:
            yield self.match_id(selector.id_, node)

    def match_attrs(self, selector, node):
        for a in selector.attrs:
            lft, op, rgt = a
            yield self.match_attr(lft, op, rgt, node)

    def match_pseudos(self, selector, d):
        for p in selector.pseudos:
            name, value = p
            if name not in self.pseudo_fns:
                raise Exception('Selector not implemented: {}'.format(name))
            yield self.pseudo_fns[name](self, d, value)

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

    def match_attr(self, lft, op, rgt, no):
        raise NotImplementedError

    def iter_data(self, data):
        raise NotImplementedError
