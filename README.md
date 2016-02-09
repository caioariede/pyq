# pyq

A command-line tool to search for Python code using jQuery-like selectors

[![PyPI version](https://badge.fury.io/py/pyqtool.svg)](https://badge.fury.io/py/pyqtool)


## Installation

    pip install pyqtool


## Usage

    pyq2 [OPTIONS] SELECTOR [PATH]  # Python 2.x
    pyq3 [OPTIONS] SELECTOR [PATH]  # Python 3.x


## Available selectors

##### Type

| Name   | Attributes                                     |
| ------ | ---------------------------------------------- |
| class  | class `name`                                   |
| def    | def `name`                                     |
| import | import `name`<br>import `name` as `name`<br>from `from` import `name`     |

##### Name

`#classname` or `#methodname`

#### Attributes

`[name=value]`, `[name!=value]`, `[name*=value]`, `[name^=value]` and `[name$=value]`

#### Pseudo-selectors

`:extends(classname)` and `:not(selector)`

#### Combinators

`parent > child`, `parent descendant`


## Examples

Search for classes that extends the `IntegerField` class:

```python
❯ pyq3 'class:extends(IntegerField)' django/forms
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
```
