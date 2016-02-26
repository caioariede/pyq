# pyq

A command-line tool to search for Python code using jQuery-like selectors

[![PyPI version](https://badge.fury.io/py/pyqtool.svg)](https://badge.fury.io/py/pyqtool)


## Installation

    pip install pyqtool

**Notice:** As the tool is still under heavy development, you may see that some features are not yet available in the version distributed over PyPI. If you want to have a fresh taste, you can get it directly from source:

    pip install https://github.com/caioariede/pyq/archive/master.zip -U

Please report any possible issues, we expect the master branch to be stable.


## Usage

    Usage: pyq3 [OPTIONS] SELECTOR [PATH]...

    Options:
    -l / --files       Only print filenames containing matches.
    --ignore-dir TEXT  Ignore directory
    -n / --no-recurse  No descending into subdirectories
    --help             Show this message and exit.

The executable name will vary depending on the Python version: `pyq2` `pyq3`


## Available selectors

##### Type selectors

| Name   | Attributes                                                            | Additional notes                                                                  |
| ------ | --------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| class  | class `name`                                                          |                                                                                   |
| def    | def `name`                                                            |                                                                                   |
| import | import `name`<br>import `name` as `name`<br>from `from` import `name` | It's also possible to match the full import using<br>the special attribute `full` |
| assign | `name` [, `name` ...] = value                                         |                                                                                   |
| call   | `name`(`arg`, `arg`, ..., `kwarg`=, `kwarg`=, ...)                    |                                                                                   |
| attr   | foo.`name`.`name`                                                     |                                                                                   |

##### ID/Name selector

| Syntax   | Applied to                               |
| -------- | ---------------------------------------- |
| #`name`  | `class`, `def`, `assign`, `call`, `attr` |


#### Attribute selectors

| Syntax            | Description                                |
| ----------------- | ------------------------------------------ |
| [`name`=`value`]  | Attribute `name` is equal to `value`       |
| [`name`!=`value`] | Attribute `name` is not equal to `value`   |
| [`name`*=`value`] | Attribute `name` contains `value`          |
| [`name`^=`value`] | Attribute `name` starts with `value`       |
| [`name`$=`value`] | Attribute `name` endswith `value`          |


#### Pseudo selectors

| Syntax                | Applies to        | Description                                        |
| --------------------- | ----------------- | -------------------------------------------------- |
| :extends(`selector`)  | `class`           | Selects classes that its bases matches `selector`  |
| :has(`selector`)      | _all_             | Selects everything that its body match `selector`  |
| :not(`selector`)      | _all_             | Selects everything that do not match `selector`    |

#### Combinators

| Syntax                | Description                            |
| --------------------- | -------------------------------------- |
| `parent` > `child`    | Select direct `child` from `parent`    |
| `parent` `descendant` | Selects all `descendant` from `parent` |


## Examples

Search for classes that extends the `IntegerField` class:

```python
❯ pyq3 'class:extends(#IntegerField)' django/forms
django/forms/fields.py:278 class FloatField(IntegerField):
django/forms/fields.py:315 class DecimalField(IntegerField):
```

Search for classes with the name `FloatField`:

```python
❯ pyq3 'class[name=FloatField]' django/forms
django/forms/fields.py:278 class FloatField(IntegerField):
```

Search for methods under the `FloatField` class:

```python
❯ pyq3 'class[name=FloatField] > def' django/forms
django/forms/fields.py:283     def to_python(self, value):
django/forms/fields.py:299     def validate(self, value):
django/forms/fields.py:308     def widget_attrs(self, widget):
```

Search for methods whose name starts with `to` under the `FloatField` class:

```python
❯ pyq3 'class[name=FloatField] > def[name^=to]' django/forms
django/forms/fields.py:283     def to_python(self, value):
```

Search for import statements importing `Counter`:

```python
❯ pyq3 'import[from=collections][name=Counter]' django/
django/apps/registry.py:5 from collections import Counter, OrderedDict, defaultdict
django/template/utils.py:3 from collections import Counter, OrderedDict
django/test/testcases.py:14 from collections import Counter
...
```

Search for classes without methods:

```python
❯ pyq3 'class:not(:has(> def))' django/core
django/core/exceptions.py:8 class FieldDoesNotExist(Exception):
django/core/exceptions.py:13 class DjangoRuntimeWarning(RuntimeWarning):
django/core/exceptions.py:17 class AppRegistryNotReady(Exception):
...
```
