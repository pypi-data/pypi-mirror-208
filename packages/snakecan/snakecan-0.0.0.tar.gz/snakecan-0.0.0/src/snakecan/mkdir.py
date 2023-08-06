import argparse
import pathlib

from snakecan.basecommand import BaseCommand


class CommandMkdir(BaseCommand):
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('directories', nargs='*')
        self.parser.add_argument('-p', '--parents', action='store_true')

    def parse_args(self, args):
        self.args = self.parser.parse_args(args)

    def run(self, stdin, stdout, stderr):
        for dir in self.args.directories:
            try:
                pathlib.Path(dir).mkdir(parents=self.args.parents, exist_ok=self.args.parents)
            except Exception as e:
                stderr.write(str(e))
                return
