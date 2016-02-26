from sizzle.match import MatchEngine

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
            matches = matcher.match_data(
                matcher.parse_selector(selector)[0], bases)
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
            for target in node.targets:
                if hasattr(target, 'id'):
                    if target.id == id_:
                        return True
                if hasattr(target, 'elts'):
                    if id_ in self._extract_names_from_tuple(target):
                        return True
                elif isinstance(target, ast.Subscript):
                    if hasattr(target.value, 'id'):
                        if target.value.id == id_:
                            return True

        if isinstance(node, ast.Call):
            return self.match_id(id_, node.func)

        if id_ == 'print' \
                and hasattr(ast, 'Print') and isinstance(node, ast.Print):
            # Python 2.x compatibility
            return True

    def match_attr(self, lft, op, rgt, node):
        values = []

        if lft == 'from':
            if isinstance(node, ast.ImportFrom) and node.module:
                values.append(node.module)

        elif lft == 'full':
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module = ''
                if isinstance(node, ast.ImportFrom):
                    if node.module:
                        module = node.module + '.'

                for n in node.names:
                    values.append(module + n.name)
                    if n.asname:
                        values.append(module + n.asname)

        elif lft == 'name':
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    if alias.asname:
                        values.append(alias.asname)
                    values.append(alias.name)

            elif isinstance(node, ast.Call):
                if hasattr(node.func, 'id'):
                    values.append(node.func.id)

            elif hasattr(ast, 'Print') and isinstance(node, ast.Print):
                values.append('print')

            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if hasattr(target, 'id'):
                        values.append(target.id)
                    elif hasattr(target, 'elts'):
                        values.extend(self._extract_names_from_tuple(target))
                    elif isinstance(target, ast.Subscript):
                        if hasattr(target.value, 'id'):
                            values.append(target.value.id)

            elif hasattr(node, lft):
                values.append(getattr(node, lft))

        elif lft in ('kwarg', 'arg'):
            if isinstance(node, ast.Call):
                if lft == 'kwarg':
                    values = [kw.arg for kw in node.keywords]
                elif lft == 'arg':
                    values = [arg.id for arg in node.args]

        if op == '=':
            return any(value == rgt for value in values)

        if op == '!=':
            return any(value != rgt for value in values)

        if op == '*=':
            return any(rgt in value for value in values)

        if op == '^=':
            return any(value.startswith(rgt) for value in values)

        if op == '$=':
            return any(value.endswith(rgt) for value in values)

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

    @classmethod
    def _extract_names_from_tuple(cls, tupl):
        r = []
        for item in tupl.elts:
            if hasattr(item, 'elts'):
                r.extend(cls._extract_names_from_tuple(item))
            else:
                r.append(item.id)
        return r
