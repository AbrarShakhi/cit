from argparse import Namespace

from cit.core.cmd_args.command import Command


class CommitCommand(Command):
    
    def execute(self, repo, args: Namespace):
        print(args)