from argparse import Namespace

from cit.core.cmd_args.command import Command


class StatusCommand(Command):
    
    def execute(self, repo, args: Namespace):
        print(args)