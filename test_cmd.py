import os
import click
import unittest

from click.testing import CliRunner
from pyq.pyq import search


def pjoin(*path):
    return os.path.join(os.path.dirname(__file__), *path)


class TestASTMatchEngine(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

        # chdir to testfiles/cmd
        self.currentdir = os.getcwd()
        os.chdir(pjoin('testfiles', 'cmd'))

    def tearDown(self):
        # restore cwd
        os.chdir(self.currentdir)

    def test_noargs(self):
        result = self.runner.invoke(search, [])

        self.assertIn('Missing argument "selector"', result.output_bytes)

    def test_nodir(self):
        result = self.runner.invoke(search, ['class'])
        output = result.output_bytes.splitlines()

        self.assertEqual(output[0], 'cmd.py:1 class Foo(object):')
        self.assertEqual(output[1], 'cmd.py:6 class Bar(object):')

    def test_file(self):
        result = self.runner.invoke(search, ['> def', 'cmd.py'])
        output = result.output_bytes.splitlines()

        self.assertEqual(output[0], 'cmd.py:11 def baz(arg1, arg2):')


if __name__ == '__main__':
    unittest.main()
