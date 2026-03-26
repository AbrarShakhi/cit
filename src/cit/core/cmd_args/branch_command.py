from argparse import Namespace

from cit.core.cmd_args.command import Command


class BranchCommand(Command):
    
    def execute(self, repo, args: Namespace):
        if not repo.cit_dir.exists():
            print("Not a cit repository")
            return

        repo.branch(args.name, args.delete)