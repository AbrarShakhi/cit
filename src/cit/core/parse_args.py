
import argparse


class ParseArgs:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Cit - A simple git clone written in python!")
        self.subparsers = self.parser.add_subparsers(dest="command", help="Available commands")

    def parse(self):
        return self.parser.parse_args()