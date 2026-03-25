from argparse import Namespace

from cit.core.cmd_args.command import Command
from cit.core.repository import Repository


class InitCommand(Command):
    
    def execute(self, repo: Repository, args: Namespace):
        if not repo.init():
            print("Repository already exists")