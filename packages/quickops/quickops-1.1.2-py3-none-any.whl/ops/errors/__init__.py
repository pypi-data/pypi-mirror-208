# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
#
# This file is part of Ops
#
# Ops is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ops is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ops.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re
import traceback

from ops.utils.text.converters import to_native, to_text


class OpsError(Exception):
    '''
    This is the base class for all errors raised from quickops code.
    '''

    def __init__(self, message="", obj=None, show_content=True, suppress_extended_error=False, orig_exc=None):
        super(OpsError, self).__init__(message)

        self._show_content = show_content
        self._suppress_extended_error = suppress_extended_error
        self._message = to_native(message)
        self.obj = obj
        self.orig_exc = orig_exc

    @property
    def message(self):
        message = [self._message]

        if self.orig_exc:
            message.append('. %s' % to_native(self.orig_exc))

        return ''.join(message)

    @message.setter
    def message(self, val):
        self._message = val

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message


class OpsPromptInterrupt(OpsError):
    '''User interrupt'''


class OpsPromptNoninteractive(OpsError):
    '''Unable to get user input'''


class OpsAssertionError(OpsError, AssertionError):
    '''Invalid assertion'''
    pass


class OpsOptionsError(OpsError):
    ''' bad or incomplete options passed '''
    pass

class OpsParserError(OpsError):
    ''' something was detected early that is wrong about a playbook or data file '''
    pass



class OpsRuntimeError(OpsError):
    ''' ops had a problem while running a playbook '''
    pass


class OpsFileNotFound(OpsRuntimeError):
    ''' a file missing failure '''

    def __init__(self, message="", obj=None, show_content=True, suppress_extended_error=False, orig_exc=None, paths=None, file_name=None):

        self.file_name = file_name
        self.paths = paths

        if message:
            message += "\n"
        if self.file_name:
            message += "Could not find or access '%s'" % to_text(self.file_name)
        else:
            message += "Could not find file"

        if self.paths and isinstance(self.paths, Sequence):
            searched = to_text('\n\t'.join(self.paths))
            if message:
                message += "\n"
            message += "Searched in:\n\t%s" % searched

        message += " on the Quickops Controller.\nIf you are using a module and expect the file to exist on the remote, see the remote_src option"

        super(OpsFileNotFound, self).__init__(message=message, obj=obj, show_content=show_content,
                                                  suppress_extended_error=suppress_extended_error, orig_exc=orig_exc)


# These Exceptions are temporary, using them as flow control until we can get a better solution.
# DO NOT USE as they will probably be removed soon.
# We will port the action modules in our tree to use a context manager instead.
class OpsAction(OpsRuntimeError):
    ''' Base Exception for Action plugin flow control '''

    def __init__(self, message="", obj=None, show_content=True, suppress_extended_error=False, orig_exc=None, result=None):

        super(OpsAction, self).__init__(message=message, obj=obj, show_content=show_content,
                                            suppress_extended_error=suppress_extended_error, orig_exc=orig_exc)
        if result is None:
            self.result = {}
        else:
            self.result = result


class OpsActionSkip(OpsAction):
    ''' an action runtime skip'''

    def __init__(self, message="", obj=None, show_content=True, suppress_extended_error=False, orig_exc=None, result=None):
        super(OpsActionSkip, self).__init__(message=message, obj=obj, show_content=show_content,
                                                suppress_extended_error=suppress_extended_error, orig_exc=orig_exc, result=result)
        self.result.update({'skipped': True, 'msg': message})


class OpsActionFail(OpsAction):
    ''' an action runtime failure'''
    def __init__(self, message="", obj=None, show_content=True, suppress_extended_error=False, orig_exc=None, result=None):
        super(OpsActionFail, self).__init__(message=message, obj=obj, show_content=show_content,
                                                suppress_extended_error=suppress_extended_error, orig_exc=orig_exc, result=result)
        self.result.update({'failed': True, 'msg': message, 'exception': traceback.format_exc()})


class OpsPluginError(OpsError):
    ''' base class for Ops plugin-related errors that do not need OpsError contextual data '''
    def __init__(self, message=None, plugin_load_context=None):
        super(OpsPluginError, self).__init__(message)
        self.plugin_load_context = plugin_load_context


class OpsPluginRemovedError(OpsPluginError):
    ''' a requested plugin has been removed '''
    pass


class OpsPluginCircularRedirect(OpsPluginError):
    '''a cycle was detected in plugin redirection'''
    pass




