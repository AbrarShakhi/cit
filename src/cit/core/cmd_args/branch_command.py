from argparse import Namespace

from cit.core.cmd_args.command import Command


class BranchCommand(Command):
    
    def execute(self, repo, args: Namespace):
        print(args)