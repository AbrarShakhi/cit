
import argparse

from cit import InitCommand
from cit import NoCommand


class ParseArgs:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Cit - A simple git clone written in python!")
        self.subparsers = self.parser.add_subparsers(dest="command", help="Available commands")
        self.COOMMANDS = {}

    def add_init_command(self):
        arg = "init"
        self.subparsers.add_parser(arg, help="Initialize a new repository")
        self.COOMMANDS[arg] = InitCommand()

    def parse_cmd(self):
        args = self.parser.parse_args()
        command = self.COOMMANDS[args]
        if not args.command or not command:
            return NoCommand(parser=self.parser)