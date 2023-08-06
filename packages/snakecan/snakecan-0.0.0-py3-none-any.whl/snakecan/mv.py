import argparse
import os
import shutil

from snakecan.basecommand import BaseCommand


class CommandMv(BaseCommand):
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('source')
        self.parser.add_argument('destination')
        self.parser.add_argument('-i', '--interactive', action='store_true')
        self.parser.add_argument('-f', '--force', action='store_true')
        self.parser.add_argument('-n', '--no-clobber', action='store_true')
        self.parser.add_argument('-t', '--move-into-dest', action='store_true')
        
    def parse_args(self, args):
        self.args = self.parser.parse_args(args)

    def run(self, stdin, stdout, stderr):
        
        src = self.args.source
        dst = self.args.destination

        if os.path.exists(dst):
            if self.args.interactive:
                answer = input(f"{dst} exists, overwrite? (y/n): ")
                if answer.lower() != 'y':
                    return
            elif self.args.no_clobber:
                return
            
        try:
            shutil.move(src, dst)
            print(f"Moved {src} to {dst}")
        except Exception as e:
            stderr.write(str(e))
