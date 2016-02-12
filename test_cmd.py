import os
import click
import unittest

from click.testing import CliRunner
from pyq.pyq import main


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
        result = self.runner.invoke(main, [])

        self.assertIn('Missing argument "selector"', result.output_bytes)

    def test_nodir(self):
        result = self.runner.invoke(main, ['def'])
        output = result.output_bytes.splitlines()

        self.assertEqual(len(output), 4)
        self.assertEqual(output[0], 'cmd.py:7  def foo(self):')
        self.assertEqual(output[1], 'cmd.py:11  def baz(arg1, arg2):')
        self.assertEqual(output[2], 'file2.py:1  def hello():')
        self.assertEqual(output[3], '.test_hidden_dir/foo.py:1  def bar():')

    def test_wildcard(self):
        result = self.runner.invoke(main, ['def', 'cmd.py', 'file2.py'])
        output = result.output_bytes.splitlines()

        self.assertEqual(len(output), 3)
        self.assertEqual(output[0], 'cmd.py:7  def foo(self):')
        self.assertEqual(output[1], 'cmd.py:11  def baz(arg1, arg2):')
        self.assertEqual(output[2], 'file2.py:1  def hello():')

    def test_file(self):
        result = self.runner.invoke(main, ['> def', 'cmd.py'])
        output = result.output_bytes.splitlines()

        self.assertEqual(output[0], 'cmd.py:11  def baz(arg1, arg2):')

    def test_print_filenames(self):
        result = self.runner.invoke(main, ['-l', 'def'])
        output = result.output_bytes.splitlines()

        self.assertEqual(output[0], 'cmd.py')
        self.assertEqual(output[1], 'file2.py')


if __name__ == '__main__':
    unittest.main()
