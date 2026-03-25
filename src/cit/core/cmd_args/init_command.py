from argparse import Namespace

from cit.core.cmd_args.command import Command


class InitCommand(Command):
    
    def execute(self, repo, args: Namespace):
        if not repo.init():
            print("Repository already exists")