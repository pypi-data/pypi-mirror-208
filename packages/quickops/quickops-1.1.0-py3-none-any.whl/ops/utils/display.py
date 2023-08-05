
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

try:
    import curses
except ImportError:
    HAS_CURSES = False
else:
    # this will be set to False if curses.setupterm() fails
    HAS_CURSES = True

import codecs
import ctypes.util
import fcntl
import getpass
import io
import logging
import os
import random
import subprocess
import sys
import termios
import textwrap
import threading
import time
import tty
import typing as t

from functools import wraps
from struct import unpack, pack

from ops import constants as C
from ops.errors import OpsError, OpsAssertionError, OpsPromptInterrupt, OpsPromptNoninteractive
from ops.utils.text.converters import to_bytes, to_text
from ops.utils.text.__init__ import text_type
from ops.utils.color import stringc
from ops.utils.singleton import Singleton

_LIBC = ctypes.cdll.LoadLibrary(ctypes.util.find_library('c'))
# Set argtypes, to avoid segfault if the wrong type is provided,
# restype is assumed to be c_int
_LIBC.wcwidth.argtypes = (ctypes.c_wchar,)
_LIBC.wcswidth.argtypes = (ctypes.c_wchar_p, ctypes.c_int)
# Max for c_int
_MAX_INT = 2 ** (ctypes.sizeof(ctypes.c_int) * 8 - 1) - 1

MOVE_TO_BOL = b'\r'
CLEAR_TO_EOL = b'\x1b[K'


def get_text_width(text):
    """Function that utilizes ``wcswidth`` or ``wcwidth`` to determine the
    number of columns used to display a text string.
    We try first with ``wcswidth``, and fallback to iterating each
    character and using wcwidth individually, falling back to a value of 0
    for non-printable wide characters.
    """
    if not isinstance(text, text_type):
        raise TypeError('get_text_width requires text, not %s' % type(text))

    try:
        width = _LIBC.wcswidth(text, _MAX_INT)
    except ctypes.ArgumentError:
        width = -1
    if width != -1:
        return width

    width = 0
    counter = 0
    for c in text:
        counter += 1
        if c in (u'\x08', u'\x7f', u'\x94', u'\x1b'):
            # A few characters result in a subtraction of length:
            # BS, DEL, CCH, ESC
            # ESC is slightly different in that it's part of an escape sequence, and
            # while ESC is non printable, it's part of an escape sequence, which results
            # in a single non printable length
            width -= 1
            counter -= 1
            continue

        try:
            w = _LIBC.wcwidth(c)
        except ctypes.ArgumentError:
            w = -1
        if w == -1:
            # -1 signifies a non-printable character
            # use 0 here as a best effort
            w = 0
        width += w

    if width == 0 and counter:
        raise EnvironmentError(
            'get_text_width could not calculate text width of %r' % text
        )

    # It doesn't make sense to have a negative printable width
    return width if width >= 0 else 0


logger = None

if getattr(C, 'DEFAULT_LOG_PATH'):
    path = C.DEFAULT_LOG_PATH
    if path and (os.path.exists(path) and os.access(path, os.W_OK)) or os.access(os.path.dirname(path), os.W_OK):
        logging.basicConfig(filename=path, level=logging.INFO,
                            format='%(asctime)s p=%(process)d  n=%(name)s | %(message)s')

        logger = logging.getLogger('ops')

    else:
        print("[WARNING]: log file at %s is not writeable and we cannot create it, aborting\n" % path, file=sys.stderr)

# map color to log levels
color_to_log_level = {C.COLOR_ERROR: logging.ERROR,
                      C.COLOR_WARN: logging.WARNING,
                      C.COLOR_OK: logging.INFO,
                      C.COLOR_SKIP: logging.WARNING,
                      C.COLOR_UNREACHABLE: logging.ERROR,
                      C.COLOR_DEBUG: logging.DEBUG,
                      C.COLOR_CHANGED: logging.INFO,
                      C.COLOR_DEPRECATE: logging.WARNING,
                      C.COLOR_VERBOSE: logging.INFO}


def _synchronize_textiowrapper(tio, lock):
    # Ensure that a background thread can't hold the internal buffer lock on a file object
    # during a fork, which causes forked children to hang. We're using display's existing lock for
    # convenience (and entering the lock before a fork).
    def _wrap_with_lock(f, lock):
        @wraps(f)
        def locking_wrapper(*args, **kwargs):
            with lock:
                return f(*args, **kwargs)

        return locking_wrapper

    buffer = tio.buffer

    # monkeypatching the underlying file-like object isn't great, but likely safer than subclassing
    buffer.write = _wrap_with_lock(buffer.write, lock)
    buffer.flush = _wrap_with_lock(buffer.flush, lock)


class Display(metaclass=Singleton):

    def __init__(self, verbosity=0):

        self._final_q = None

        # NB: this lock is used to both prevent intermingled output between threads and to block writes during forks.
        # Do not change the type of this lock or upgrade to a shared lock (eg multiprocessing.RLock).
        self._lock = threading.RLock()

        self.columns = None
        self.verbosity = verbosity
        self._warns = {}

        self._set_column_width()

        try:
            # NB: we're relying on the display singleton behavior to ensure this only runs once
            _synchronize_textiowrapper(sys.stdout, self._lock)
            _synchronize_textiowrapper(sys.stderr, self._lock)
        except Exception as ex:
            self.warning(f"failed to patch stdout/stderr for fork-safety: {ex}")

        codecs.register_error('_replacing_warning_handler', self._replacing_warning_handler)
        try:
            sys.stdout.reconfigure(errors='_replacing_warning_handler')
            sys.stderr.reconfigure(errors='_replacing_warning_handler')
        except Exception as ex:
            self.warning(f"failed to reconfigure stdout/stderr with custom encoding error handler: {ex}")

        self.setup_curses = False

    def _replacing_warning_handler(self, exception):
        # TODO: This should probably be deferred until after the current display is completed
        #       this will require some amount of new functionality
        self.deprecated(
            'Non UTF-8 encoded data replaced with "?" while displaying text to stdout/stderr, this is temporary and will become an error',
            version='2.18',
        )
        return '?', exception.end


    def display(self, msg, color=None, stderr=False, screen_only=False, log_only=False, newline=True):
        """ Display a message to the user
        Note: msg *must* be a unicode string to prevent UnicodeError tracebacks.
        """

        if not isinstance(msg, str):
            raise TypeError(f'Display message must be str, not: {msg.__class__.__name__}')

        if self._final_q:
            # If _final_q is set, that means we are in a WorkerProcess
            # and instead of displaying messages directly from the fork
            # we will proxy them through the queue
            return self._final_q.send_display(msg, color=color, stderr=stderr,
                                              screen_only=screen_only, log_only=log_only, newline=newline)

        nocolor = msg

        if not log_only:

            has_newline = msg.endswith(u'\n')
            if has_newline:
                msg2 = msg[:-1]
            else:
                msg2 = msg

            if color:
                msg2 = stringc(msg2, color)

            if has_newline or newline:
                msg2 = msg2 + u'\n'

            if not stderr:
                fileobj = sys.stdout
            else:
                fileobj = sys.stderr

            with self._lock:
                fileobj.write(msg2)

        if logger and not screen_only:
            msg2 = nocolor.lstrip('\n')

            lvl = logging.INFO
            if color:
                try:
                    lvl = color_to_log_level[color]
                except KeyError:
                    # this should not happen, but JIC
                    raise OpsAssertionError('Invalid color supplied to display: %s' % color)
            # actually log
            logger.log(lvl, msg2)


    def warning(self, msg, formatted=False):

        if not formatted:
            new_msg = "[WARNING]: %s" % msg
            wrapped = textwrap.wrap(new_msg, self.columns)
            new_msg = "\n".join(wrapped) + "\n"
        else:
            new_msg = "\n[WARNING]: \n%s" % msg

        if new_msg not in self._warns:
            self.display(new_msg, color=C.COLOR_WARN, stderr=True)
            self._warns[new_msg] = 1

    def system_warning(self, msg):
        if C.SYSTEM_WARNINGS:
            self.warning(msg)

    def banner(self, msg, color=None, cows=True):
        '''
        Prints a header-looking line with cowsay or stars with length depending on terminal width (3 minimum)
        '''
        msg = to_text(msg)

        msg = msg.strip()
        try:
            star_len = self.columns - get_text_width(msg)
        except EnvironmentError:
            star_len = self.columns - len(msg)
        if star_len <= 3:
            star_len = 3
        stars = u"*" * int(star_len/2)
        self.display(u"\n%s %s %s" % (stars,msg, stars), color=color)


    def error(self, msg, wrap_text=True):
        if wrap_text:
            new_msg = u"\n[ERROR]: %s" % msg
            wrapped = textwrap.wrap(new_msg, self.columns)
            new_msg = u"\n".join(wrapped) + u"\n"
        else:
            new_msg = u"ERROR! %s" % msg
        self.display(new_msg, color=C.COLOR_ERROR, stderr=True)

    def _set_column_width(self):
        if os.isatty(1):
            tty_size = unpack('HHHH', fcntl.ioctl(1, termios.TIOCGWINSZ, pack('HHHH', 0, 0, 0, 0)))[1]
        else:
            tty_size = 0
        self.columns = max(79, tty_size - 1)