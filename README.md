# pyq
Search Python code by using jQuery-like selectors

## Installation (not yet on PyPI)

    pip install https://github.com/caioariede/pyq/archive/master.zip

## Usage

    pyq 'selector' [directory]

## Examples

    $ pyq 'class:extends(forms.Widget)' django/forms
    django/forms/fields.py:278 class FloatField(IntegerField):
    django/forms/fields.py:315 class DecimalField(IntegerField):

    $ pyq 'class[name=FloatField]' django/forms
    django/forms/fields.py:278 class FloatField(IntegerField):
    
    $ pyq 'class[name=FloatField] > def' django/forms
    django/forms/fields.py:283     def to_python(self, value):
    django/forms/fields.py:299     def validate(self, value):
    django/forms/fields.py:308     def widget_attrs(self, widget):
