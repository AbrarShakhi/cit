from argparse import Namespace

from cit.core.cmd_args.command import Command
from cit.core.repository import Repository


class CheckoutCommand(Command):
    
    def execute(self, repo: Repository, args: Namespace):
        if not repo.git_dir.exists():
            print("Not a git repository")
            return
        
        repo.checkout(args.branch, args.create_branch)