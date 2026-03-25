from argparse import Namespace

from cit.core.cmd_args.command import Command


class BranchCommand(Command):
    
    def execute(self, repo, args: Namespace):
        if not repo.git_dir.exists():
            print("Not a git repository")
            return

        repo.branch(args.name, args.delete)