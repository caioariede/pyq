# Changelog

## Current

### New features

* Added `--expand` option that allows showing multiples matches in the same
  line

## 0.0.6 / 2016-02-26

### New features

* Added type `attr` (eg. `attr#foo` will match `a.foo.bar` and `a.bar.foo`)
* Added support for wildcards
* Added special attribute `full` to match imports: `import[full=x.z]` will
  match `from x import y as z`
* Added ability to match calls with certain `arg` or `kwarg` (eg.
  `call[arg=foo]` will match `bar(x, y, foo)`; `[kwarg=bar]` will match
  `foo(bar=1, z=2)`
* Added `--ignore-dir` and `--no-recurse` options

### Bug fixed

* Fixed bug when `node.body` is not an iterator (eg. lambdas)


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
