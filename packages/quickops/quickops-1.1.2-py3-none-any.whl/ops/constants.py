
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


def set_constant(name, value, export=vars()):
    ''' sets constants '''
    export[name] = value



# CONSTANTS
OPS_NOCOLOR = False
OPS_FORCE_COLOR = True
#DEFAULT_LOG_PATH = str(importlib.resources.files('ops')) + '/log'
DEFAULT_LOG_PATH = ""
COLOR_ERROR = 'red'
COLOR_WARN = 'yellow'
COLOR_OK = 'black'
COLOR_SKIP = 'black'
COLOR_UNREACHABLE = 'black'
COLOR_DEBUG = 'black'
COLOR_CHANGED = 'black'
COLOR_DEPRECATE = 'black'
COLOR_VERBOSE = 'black'

# http://nezzen.net/2008/06/23/colored-text-in-python-using-ansi-escape-sequences/
COLOR_CODES = {
    'black': u'0;30', 'bright gray': u'0;37',
    'blue': u'0;34', 'white': u'1;37',
    'green': u'0;32', 'bright blue': u'1;34',
    'cyan': u'0;36', 'bright green': u'1;32',
    'red': u'0;31', 'bright cyan': u'1;36',
    'purple': u'0;35', 'bright red': u'1;31',
    'yellow': u'0;33', 'bright purple': u'1;35',
    'dark gray': u'1;30', 'bright yellow': u'1;33',
    'magenta': u'0;35', 'bright magenta': u'1;35',
    'normal': u'0',
}


# Generate constants from config
#for setting in config.get_configuration_definitions():
 #   set_constant(setting, config.get_config_value(setting, variables=vars()))

#for warn in config.WARNINGS:
 #   _warning(warn)