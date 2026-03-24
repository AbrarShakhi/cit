from argparse import Namespace

from .command import Command


class InitCommand(Command):
    
    def execute(self, repo, args: Namespace):
        pass