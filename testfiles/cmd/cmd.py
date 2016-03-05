class Foo(object):
    pass


@decorator
class Bar(object):
    def foo(self):
        pass


def baz(arg1, arg2):
    pass


foo() | bar()
