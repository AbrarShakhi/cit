from argparse import Namespace

from cit.core.cmd_args.command import Command
from cit.core.repository import Repository


class AddCommand(Command):
    
    def execute(self, repo: Repository, args: Namespace):
        if not repo.cit_dir.exists():
            print("fatal: not a cit repository (or any of the parent directories): .cit")
            return

        for path in args.paths:
            repo.add_path(path)