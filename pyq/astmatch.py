from sizzle.match import MatchEngine

import ast
import astor


class ASTMatchEngine(MatchEngine):
    def __init__(self):
        super().__init__()
        self.register_pseudo('extends', self.pseudo_extends)

    def match(self, selector, filename):
        module = astor.parsefile(filename)
        for match in super().match(selector, module.body):
            lineno = match.lineno
            if isinstance(match, (ast.ClassDef, ast.FunctionDef)):
                for d in match.decorator_list:
                    lineno += 1
            yield match, lineno

    @staticmethod
    def pseudo_extends(matcher, node, value):
        for base in node.bases:
            base_str = astor.to_source(base).rstrip()
            if base_str == value:
                return True
            elif '.' in base_str and value in base_str:
                parts = base_str.split('.')
                if value in parts:
                    return True

    def match_type(self, typ, node):
        if typ == 'class':
            return isinstance(node, ast.ClassDef)

        if typ == 'def':
            return isinstance(node, ast.FunctionDef)

    def match_id(self, id_, node):
        return node.name == id_

    def match_attr(self, lft, op, rgt, node):
        value = getattr(node, lft, None)

        if op == '=':
            return value == rgt

        if op == '!=':
            return value != rgt

        if op == '*=':
            return rgt in value

        if op == '^=':
            return value.startswith(rgt)

        if op == '$=':
            return value.endswith(rgt)

        raise Exception('Attribute operator {} not implemented'.format(op))

    def iter_data(self, data):
        for node in data:
            yield node, getattr(node, 'body', None)
