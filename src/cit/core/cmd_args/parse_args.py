
import argparse
from typing import Self

from cit.core.cmd_args.add_command import AddCommand
from cit.core.cmd_args.branch_command import BranchCommand
from cit.core.cmd_args.checkout_command import CheckoutCommand
from cit.core.cmd_args.commit_command import CommitCommand
from cit.core.cmd_args.init_command import InitCommand
from cit.core.cmd_args.log_command import LogCommand
from cit.core.cmd_args.no_command import NoCommand
from cit.core.cmd_args.command import Command
from cit.core.cmd_args.status_command import StatusCommand


class ParseArgs:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Cit - A simple git clone written in python!")
        self.subparsers = self.parser.add_subparsers(dest="command", help="Available commands")
        self.COOMMANDS = {}
        self.args = None


    def add_init_command(self) -> Self:
        arg = "init"
        self.subparsers.add_parser(arg, help="Initialize a new repository")
        self.COOMMANDS[arg] = InitCommand()
        return self


    def add_add_command(self) -> Self:
        arg = "add"
        add_parser = self.subparsers.add_parser(arg, help="Add file contents to the index")
        add_parser.add_argument("paths", nargs="+", help="Files and directories to add")
        self.COOMMANDS[arg] = AddCommand()
        return self


    def add_commit_command(self) -> Self:
        arg = "commit"
        commit_parser = self.subparsers.add_parser(arg, help="Record changes to the repository")
        commit_parser.add_argument("-m", "--message", help="Commit message", required=True)
        self.COOMMANDS[arg] = CommitCommand()
        return self


    def add_checkout_command(self) -> Self:
        arg = "checkout"
        checkout_parser = self.subparsers.add_parser(arg, help="Move/Create a new branch")
        checkout_parser.add_argument("branch", help="Branch to switch to")
        checkout_parser.add_argument("-b", "--create-branch", action="store_true", help="Create and switch to a new branch")
        self.COOMMANDS[arg] = CheckoutCommand()
        return self


    def add_branch_command(self) -> Self:
        arg = "branch"
        branch_parser = self.subparsers.add_parser(arg, help="List or manage branches")
        branch_parser.add_argument("name", nargs="?")
        branch_parser.add_argument("-d", "--delete", action="store_true", help="Delete the branch")
        self.COOMMANDS[arg] = BranchCommand()
        return self


    def add_log_command(self) -> Self:
        arg = "log"
        log_parser = self.subparsers.add_parser(arg, help="Show commit logs")
        log_parser.add_argument("-n", "--max-count", type=int, default=10, help="Limit commits shown")
        self.COOMMANDS[arg] = LogCommand()
        return self


    def add_status_command(self) -> Self:
        arg = "status"
        self.subparsers.add_parser(arg, help="Show the working tree status")
        self.COOMMANDS[arg] = StatusCommand()
        return self

    def parse(self) -> argparse.Namespace:
        if self.args is None:
            self.args = self.parser.parse_args()
        return self.args


    def parse_cmd(self) -> Command:
        args = self.parse()
        command_name = args.command
        command = self.COOMMANDS.get(command_name)
        if not command_name or not command:
            return NoCommand(parser=self.parser)
        
        return command