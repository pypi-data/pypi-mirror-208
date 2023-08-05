from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

#ops.cli needs to be imported first, to ensure the source bin/* scripts run that code first
from ops.cli import CLI
from ops import constants as C
from ops.cli.arguments import option_helpers as opt_help
from ops.errors import OpsError, OpsOptionsError, OpsParserError
from ops.utils.text.converters import to_text
from ops.utils.display import Display

display = Display()


class OpsCLI(CLI):
    ''' this command allows you to create a template entity for a specific DevOps tool'''

    name = 'quickops'

    def init_parser(self):
        ''' create an options parser'''
        super(OpsCLI, self).init_parser(usage='%prog  [options]',
                                          desc="Run a command to create a template entity for a specific tool",
                                          epilog="Read instructions carefully")


        opt_help.add_context_argument(self.parser)
        opt_help.add_command_argument(self.parser)

    def post_process_args(self, options):
        '''Post process and validate options '''

        options = super(OpsCLI, self).post_process_args(options)

        display.verbosity = options.verbosity
        self.validate_conflicts(options, runas_opts=True, fork_opts=True)

        return options


    def run(self):
        ''' execute command '''
        super(OpsCLI, self).run()


def main(args=None):
    OpsCLI.cli_executor(args)


if __name__ == '__main__':
    main()