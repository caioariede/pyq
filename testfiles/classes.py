class Foo(object):
    def bar(self):
        pass

    def baz(self):
        pass


class Bar(object):
    test = None


class Bang:
    class Baz(object):
        def bar(self):
            x = [0]
            x[0] = 1


import dummy_import
