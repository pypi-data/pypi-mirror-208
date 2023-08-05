from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import operator
import argparse
import os
import os.path
import sys
import shutil
from importlib_resources import files
import cowsay

from ops.utils.text.converters import to_native
from ops.utils.display import Display
from ops.release import __version__

display = Display()

docker_options = "docker - c++,npm,python,springboot\n"
gitlab_options = "gitlab - django,docker,gradle,maven,npm\n"
jenkins_options = "docker - django,docker,gradle,maven,npm,sonarqube\n"

class SortingHelpFormatter(argparse.HelpFormatter):
    def add_arguments(self, actions):
        actions = sorted(actions, key=operator.attrgetter('option_strings'))
        super(SortingHelpFormatter, self).add_arguments(actions)


class OpsVersion(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        ops_version = to_native(version(getattr(parser, 'prog')))
        cowsay.fox(ops_version)
        parser.exit()


class runCommandAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        context = namespace.context[0]
        command = values[0]

        if context == 'jenkins':
            if command not in ['django','docker','gradle','maven','npm','sonarqube']:
                display.error("chooose from ['django','docker','gradle','maven','npm','sonarqube']")
                parser.exit(1, "")
                return

            template_name = 'Jenkinsfile.groovy'

        if context == 'gitlab':
            if command not in ['django','docker','gradle','maven','npm']:
                display.error("chooose from ['django','docker','gradle','maven','npm']")
                parser.exit(1, "")
                return

            template_name = 'gitlab-ci.yml'

        if context == 'docker':
            if command not in ['c++','npm','python','springboot']:
                display.error("chooose from ['c++','npm','python','springboot']")
                parser.exit(1, "")
                return

            template_name = 'Dockerfile'

        template = os.path.join(str(files('ops.entities')), context, command, template_name)
        user_cwd = os.getcwd()
        shutil.copy(template, user_cwd)

        display.display("Done!","green")

        parser.exit()


def version(prog=None):
    """ return ops version """
    if prog:
        result = ["{0} {1} ".format(prog, __version__)]
    else:
        result = [__version__]


    result.append("  executable location = %s" % sys.argv[0])
    result.append("  python version = %s (%s)" % (''.join(sys.version.splitlines()), to_native(sys.executable)))
    return "\n".join(result)



def create_base_parser(prog, usage="", desc=None, epilog=None):
    """
    Create an options parser
    """
    parser = argparse.ArgumentParser(
        prog=prog,
        formatter_class=SortingHelpFormatter,
        epilog=epilog,
        description=desc,
        conflict_handler='resolve',
    )
    version_help = "show program's version number and executable location"

    parser.add_argument('--version', action=OpsVersion, nargs=0, help=version_help)
    return parser

def add_context_argument(parser):
    """Add context to choose DevOps tool"""
    parser.add_argument('context', metavar='gitlab|jenkins|docker', choices=['gitlab', 'jenkins', 'docker'],
                        action='store', nargs=1,
                        help="generate pipeline or dockerfile")

def add_command_argument(parser):
    """Add argument to choose language/framework"""
    parser.add_argument('command', metavar='c++|npm|python|springboot|django|docker|gradle|maven|sonarqube',
                        choices=['c++', 'npm', 'python', 'springboot', 'django', 'docker', 'gradle', 'maven',
                                 'sonarqube'],
                        action=runCommandAction, nargs=1,
                        help="choose language/framework\n" + docker_options + gitlab_options + jenkins_options)