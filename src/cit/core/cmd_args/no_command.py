from argparse import ArgumentParser, Namespace

from cit.core.cmd_args.command import Command
from cit.core.repository import Repository


class NoCommand(Command):

    def __init__(self, parser: ArgumentParser):
        super().__init__()
        self.parser = parser
    
    def execute(self, repo: Repository, args: Namespace):
        self.parser.print_help()