from selector import Selector


class MatchEngine(object):
    pseudo_fns = {}

    def __init__(self):
        self.register_pseudo('not', self.pseudo_not)

    def register_pseudo(self, name, fn):
        self.pseudo_fns[name] = fn

    @staticmethod
    def pseudo_not(matcher, node, value):
        return not matcher.match_node(Selector.parse(value)[0], node)

    def match(self, selector, data):
        selectors = Selector.parse(selector)
        for selector in selectors:
            yield from self.match_data(selector, data)

    def match_data(self, selector, data):
        for node, body in self._iter_data(data):
            match = self.match_node(selector, node)

            if match:
                next_selector = selector.next_selector
                if next_selector:
                    if body:
                        yield from self.match_data(next_selector, body)
                else:
                    yield node

            if body and not selector.combinator == Selector.CHILD:
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
