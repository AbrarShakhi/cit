from argparse import ArgumentParser, Namespace

from cit.core.cmd_args.command import Command


class NoCommand(Command):

    def __init__(self, parser: ArgumentParser):
        super().__init__()
        self.parser = parser
    
    def execute(self, repo, args: Namespace):
        self.parser.print_help()