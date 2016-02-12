from foo import bar  # noqa
from foo import bar as bar2, xyz  # noqa
from foo.baz import bang  # noqa
from . import x

import example as example2  # noqa
import foo.baz  # noqa
