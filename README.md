# pyq
Search Python code by using jQuery-like selectors

## Installation (not yet on PyPI)

    pip install https://github.com/caioariede/pyq/archive/master.zip

## Usage

    pyq [OPTIONS] SELECTOR [PATH]

## Examples

Search for classes that extends the `IntegerField` class.

```python
❯ pyq 'class:extends(IntegerField)' django/forms
django/forms/fields.py:278 class FloatField(IntegerField):
django/forms/fields.py:315 class DecimalField(IntegerField):
```

Search for classes with the name `FloatField`.

```python
❯ pyq 'class[name=FloatField]' django/forms
django/forms/fields.py:278 class FloatField(IntegerField):
```

Search for methods under the `FloatField` class.

```python
❯ pyq 'class[name=FloatField] > def' django/forms
django/forms/fields.py:283     def to_python(self, value):
django/forms/fields.py:299     def validate(self, value):
django/forms/fields.py:308     def widget_attrs(self, widget):
```

Search for methods whose name starts with `to` under the `FloatField` class.

```python
❯ pyq 'class[name=FloatField] > def[name^=to]' django/forms
django/forms/fields.py:283     def to_python(self, value):
```

Search for import statements importing `Counter`.

```python
❯ pyq 'import[from=collections][name=Counter]' django/
django/apps/registry.py:5 from collections import Counter, OrderedDict, defaultdict
django/template/utils.py:3 from collections import Counter, OrderedDict
django/test/testcases.py:14 from collections import Counter
```
