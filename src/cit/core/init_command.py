from argparse import Namespace

from cit.core.command import Command


class InitCommand(Command):
    
    def execute(self, repo, args: Namespace):
        print(args)