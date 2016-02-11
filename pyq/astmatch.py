from sizzle.match import MatchEngine
from sizzle.selector import Selector

import ast
import astor


class ASTMatchEngine(MatchEngine):
    def __init__(self):
        super(ASTMatchEngine, self).__init__()
        self.register_pseudo('extends', self.pseudo_extends)

    def match(self, selector, filename):
        module = astor.parsefile(filename)
        for match in super(ASTMatchEngine, self).match(selector, module.body):
            lineno = match.lineno
            if isinstance(match, (ast.ClassDef, ast.FunctionDef)):
                for d in match.decorator_list:
                    lineno += 1
            yield match, lineno

    @staticmethod
    def pseudo_extends(matcher, node, value):
        if not isinstance(node, ast.ClassDef):
            return False

        if not value:
            return node.bases == []

        bases = node.bases
        selectors = value.split(',')

        for selector in selectors:
            matches = matcher.match_data(Selector.parse(selector)[0], bases)
            if any(matches):
                return True

    def match_type(self, typ, node):
        if typ == 'class':
            return isinstance(node, ast.ClassDef)

        if typ == 'def':
            return isinstance(node, ast.FunctionDef)

        if typ == 'import':
            return isinstance(node, (ast.Import, ast.ImportFrom))

        if typ == 'assign':
            return isinstance(node, ast.Assign)

        if typ == 'attr':
            return isinstance(node, ast.Attribute)

        if typ == 'call':
            if isinstance(node, ast.Call):
                return True

            # Python 2.x compatibility
            return hasattr(ast, 'Print') and isinstance(node, ast.Print)

    def match_id(self, id_, node):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
            return node.name == id_

        if isinstance(node, ast.Name):
            return node.id == id_

        if isinstance(node, ast.Attribute):
            return node.attr == id_

        if isinstance(node, ast.Assign):
            return any(self.match_id(id_, t) for t in node.targets)

        if isinstance(node, ast.Call):
            return self.match_id(id_, node.func)

        if id_ == 'print' \
                and hasattr(ast, 'Print') and isinstance(node, ast.Print):
            # Python 2.x compatibility
            return True

    def match_attr(self, lft, op, rgt, node):
        if lft == 'from':
            if isinstance(node, ast.ImportFrom):
                lft = 'module'
        elif lft == 'name':
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    if alias.asname:
                        if self.match_attr('asname', op, rgt, alias):
                            return True
                    if self.match_attr('name', op, rgt, alias):
                        return True
                return False

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
            for n in self.iter_node(node):
                yield n

    def iter_node(self, node):
        silence = (ast.Expr,)

        if not isinstance(node, silence):
            try:
                body = node.body

                # check if is iterable
                list(body)

            except TypeError:
                body = [node.body]

            except AttributeError:
                body = None

            yield node, body

        if hasattr(node, 'value'):
            # reversed is used here so matches are returned in the
            # sequence they are read, eg.: foo.bar.bang
            for n in reversed(list(self.iter_node(node.value))):
                yield n
