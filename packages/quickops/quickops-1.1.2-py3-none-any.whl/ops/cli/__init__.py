# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import locale
import os
import sys

# Restrict Python version
if sys.version_info < (3, 1):
    raise SystemExit(
        'ERROR: Quickops requires Python 3.11 or newer on the controller. '
        'Current version: %s' % ''.join(sys.version.splitlines())
    )


def check_blocking_io():
    """Check stdin/stdout/stderr to make sure they are using blocking IO."""
    handles = []

    for handle in (sys.stdin, sys.stdout, sys.stderr):
        try:
            fd = handle.fileno()
        except Exception:
            continue
        if not os.get_blocking(fd):
            handles.append(getattr(handle, 'name', None) or '#%s' % fd)

    if handles:
        raise SystemExit('ERROR: Quickops requires blocking IO on stdin/stdout/stderr. '
                         'Non-blocking file handles detected: %s' % ', '.join(_io for _io in handles))


check_blocking_io()


def initialize_locale():
    """Set the locale and ensure encoding is UTF-8.
    """
    try:
        locale.setlocale(locale.LC_ALL, '')
        dummy, encoding = locale.getlocale()
    except (locale.Error, ValueError) as e:
        raise SystemExit(
            'ERROR: Quickops could not initialize the preferred locale: %s' % e
        )

    if not encoding or encoding.lower() not in ('utf-8', 'utf8'):
        raise SystemExit('ERROR: Quickops requires the locale encoding to be UTF-8; Detected %s.' % encoding)

    fs_enc = sys.getfilesystemencoding()
    if fs_enc.lower() != 'utf-8':
        raise SystemExit('ERROR: Quickops requires the filesystem encoding to be UTF-8; Detected %s.' % fs_enc)


initialize_locale()

import errno
import getpass
import subprocess
import traceback
from abc import ABC, abstractmethod
from pathlib import Path

try:
    from ops.utils.display import Display

    display = Display()
except Exception as e:
    print('ERROR: %s' % e, file=sys.stderr)
    # input/output error
    sys.exit(5)

from ops.errors import OpsError, OpsOptionsError, OpsParserError
from ops.cli.arguments import option_helpers as opt_help
from ops.utils.text.converters import to_bytes, to_text
from ops.release import __version__

try:
    import argcomplete

    HAS_ARGCOMPLETE = True
except ImportError:
    HAS_ARGCOMPLETE = False


class CLI(ABC):
    ''' code behind bin/ops* programs '''

    # PAGER = C.config.get_config_value('PAGER')

    # -F (quit-if-one-screen) -R (allow raw ansi control chars)
    # -S (chop long lines) -X (disable termcap init and de-init)
    LESS_OPTS = 'FRSX'
    SKIP_INVENTORY_DEFAULTS = False

    def __init__(self, args, callback=None):
        """
        Base init method for all command line programs
        """

        if not args:
            raise ValueError('A non-empty list for args is required')

        self.args = args
        self.parser = None
        self.callback = callback

    @abstractmethod
    def run(self):
        """Run the quickops command
        Subclasses must implement this method.  It does the actual work of
        running an quickops command.
        """
        self.parse()

    # TODO: remove the now unused args
    def validate_conflicts(self, op, runas_opts=False, fork_opts=False):
        ''' check for conflicting options '''

        if fork_opts:
            if op.forks < 1:
                self.parser.error("The number of processes (--forks) must be >= 1")

        return op

    @abstractmethod
    def init_parser(self, usage="", desc=None, epilog=None):
        """
        Create an options parser
        """
        self.parser = opt_help.create_base_parser(self.name, usage=usage, desc=desc, epilog=epilog)

    def parse(self):
        """Parse the command line args
        """
        self.init_parser()

        if HAS_ARGCOMPLETE:
            argcomplete.autocomplete(self.parser)

        try:
            options = self.parser.parse_args(self.args[1:])
        except SystemExit as ex:
            if ex.code != 0:
                self.parser.exit(status=2, message=" \n%s" % self.parser.format_help())
            raise
        options = self.post_process_args(options)

    @classmethod
    def cli_executor(cls, args=None):
        if args is None:
            args = sys.argv

        display.banner("QuickOps")

        try:
            try:
                args = [to_text(a, errors='surrogate_or_strict') for a in args]
            except UnicodeError:
                display.error(
                    'Command line args are not in utf-8, unable to continue. Quickops currently only understands utf-8')
                display.display(u"The full traceback was:\n\n%s" % to_text(traceback.format_exc()))
                exit_code = 6
            else:
                cli = cls(args)
                exit_code = cli.run()

        except OpsOptionsError as e:
            cli.parser.print_help()
            display.error(to_text(e), wrap_text=False)
            exit_code = 5
        except OpsParserError as e:
            display.error(to_text(e), wrap_text=False)
            exit_code = 4
        except OpsError as e:
            display.error(to_text(e), wrap_text=False)
            exit_code = 1
        except KeyboardInterrupt:
            display.error("User interrupted execution")
            exit_code = 99
        except Exception as e:
            display.display(u"the full traceback was:\n\n%s" % to_text(traceback.format_exc()))
            exit_code = 250

        sys.exit(exit_code)
