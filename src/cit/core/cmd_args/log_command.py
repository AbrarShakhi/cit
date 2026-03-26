from argparse import Namespace

from cit.core.cmd_args.command import Command


class LogCommand(Command):
    
    def execute(self, repo, args: Namespace):
        if not repo.git_dir.exists():
            print("Not a cit repository")
            return

        repo.log(args.max_count)