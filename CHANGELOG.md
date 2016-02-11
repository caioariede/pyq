# Changelog

## 0.0.5 / 2016-02-11

### New features

* Added CHANGELOG.md
* Added support for the type `assign` (eg. `assign#foo` will match `foo = 1`)
* Changed `extends()` pseudo-selector to receive a selector as argument
* Added support for the type `call` (eg. `call#foo` will match `foo(1)`)


### Bug fixes

* Fixed bug when using `:extends()` without the type `class` specified
* Fixed bug when trying to match `#name` with a node that doesn't have a name
  attribute


## 0.0.4 / 2016-02-10

* Added `-l/--files` option to print only files names


## 0.0.3 / 2016-02-09

* Added support for Python 2


## 0.0.2 / 2016-02-08

* Changed package name from pyq to pyqtool, to avoid conflicts w/ existing
  packages


## 0.0.1 / 2016-02-07

* Initial release
