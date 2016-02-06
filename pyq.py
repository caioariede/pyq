"""

.function_name  | .name:fn
.class_name     | .name:cls

fn[name=foo]
cls[name=foo][extends=bar]A
import[from=os.path]

.class_name > .method_name



"""

import click
import os
import astor
import ast


class BaseSObj(object):
    def __init__(self, sel):
        self.sel = sel


class ClassSObj(BaseSObj):
    def match(self, ast_node):
        return self.sel[1:] == ast_node.name


@click.command()
@click.argument('selector')
@click.argument('path', type=click.Path(exists=True), default='.')
def search(selector, path):
    path = click.format_filename(path)
    sobjs = parse_selector(selector)

    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for fn in files:
                if fn.endswith('.py'):
                    fn = os.path.join(root, fn)
                    if match(sobjs, fn):
                        print(fn)
    elif path.endswith('.py'):
        fn = path
        if match(sobjs, fn):
            print(fn)


def parse_selector(selstr):
    sobjs = []
    selectors = selstr.split(',')
    for sel in selectors:
        if sel.startswith('.'):
            sobjs.append(ClassSObj(sel))
    return sobjs


def match(sobjs, fn):
    mod = astor.code_to_ast.parse_file(fn)
    for ast_node in mod.body:
        if match_node(sobjs, ast_node):
            return True
    return False


def match_node(sobjs, ast_node):
    if isinstance(ast_node, (ast.ClassDef, ast.FunctionDef)):
        for sobj in sobjs:
            if isinstance(sobj, ClassSObj) and sobj.match(ast_node):
                return True
    return False


if __name__ == '__main__':
    search()
