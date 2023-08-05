
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re
import sys

from ops import constants as C

OPS_COLOR = True
if C.OPS_NOCOLOR:
    OPS_COLOR = False
elif not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
    OPS_COLOR = False
else:
    try:
        import curses
        curses.setupterm()
        if curses.tigetnum('colors') < 0:
            OPS_COLOR = False
    except ImportError:
        # curses library was not found
        pass
    except curses.error:
        # curses returns an error (e.g. could not find terminal)
        OPS_COLOR = False

if C.OPS_FORCE_COLOR:
    OPS_COLOR = True


def parsecolor(color):
    """SGR parameter string for the specified color name."""
    matches = re.match(r"color(?P<color>[0-9]+)"
                       r"|(?P<rgb>rgb(?P<red>[0-5])(?P<green>[0-5])(?P<blue>[0-5]))"
                       r"|gray(?P<gray>[0-9]+)", color)
    if not matches:
        return C.COLOR_CODES[color]
    if matches.group('color'):
        return u'38;5;%d' % int(matches.group('color'))
    if matches.group('rgb'):
        return u'38;5;%d' % (16 + 36 * int(matches.group('red')) +
                             6 * int(matches.group('green')) +
                             int(matches.group('blue')))
    if matches.group('gray'):
        return u'38;5;%d' % (232 + int(matches.group('gray')))


def stringc(text, color, wrap_nonvisible_chars=False):
    """String in color."""

    if OPS_COLOR:
        color_code = parsecolor(color)
        fmt = u"\033[%sm%s\033[0m"
        if wrap_nonvisible_chars:
            fmt = u"\001\033[%sm\002%s\001\033[0m\002"
        return u"\n".join([fmt % (color_code, t) for t in text.split(u'\n')])
    else:
        return text

