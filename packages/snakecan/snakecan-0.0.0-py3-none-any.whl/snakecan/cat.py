import argparse
import sys

from snakecan import util
from snakecan.basecommand import BaseCommand


class CommandCat(BaseCommand):
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('files', nargs='*')
        self.parser.add_argument('-b', '--show-numbers-without-blanks', action='store_true', help='display I at each tab')
        self.parser.add_argument('-e', '--show-ends', action='store_true', help='display $ at end of each line')
        self.parser.add_argument('-n', '--show-numbers', action='store_true', help='number all output lines')
        self.parser.add_argument('-t', '--show-tabs', action='store_true', help='display I at each tab')
        self.parser.add_argument('-v', '--show-nonprinting', action='store_true', help='use ^ and M- notation, except for LFD and TAB')

    def parse_args(self, args):
        self.args = self.parser.parse_args(args)

        # If we pass -e, we must pass -v
        if self.args.show_ends:
            self.args.show_nonprinting = True
        
        # If we pass -b, we must pass -n
        if self.args.show_numbers_without_blanks:
            self.args.show_numbers = True

    def run(self, stdin, stdout, stderr):
        line_num = 1
        ended_with_newline = True
        for filename in self.args.files:
            try:
                with open(filename, 'rb') as f:
                    for line in f:
                        original_line = line

                        # Write non printing characters
                        if self.args.show_nonprinting:
                            chars = []
                            for c in line:
                                c = chr(c)

                                if c == '\n':
                                    # Show endlines
                                    if self.args.show_ends:
                                        chars.append('$')
                                elif c == '\t':
                                    # Show tabs
                                    if self.args.show_tabs:
                                        chars.append('^I')
                                        continue
                                else:
                                    # Show nonprinting 
                                    if not util.isascii(c):
                                        chars.append('M-')
                                        c = util.toascii(c)
                                    if util.iscntrl(c):
                                        chars.append('^')
                                        chars.append('?' if c == 127 else chr( util.chartoint(c) | 0x40 ) )
                                        continue
                                chars.append(c)
                            line = ''.join(chars)
                        
                        # Write line numbers
                        if self.args.show_numbers and ended_with_newline: 
                            # Check if we need to ignore a blank line
                            if not self.args.show_numbers_without_blanks or ( len(original_line) >= 1 and original_line[0] != ord('\n') ):
                                line = f'{line_num:6}  ' + line
                                line_num += 1
                        ended_with_newline = True

                        # Write out the line!
                        stdout.write(line)

                    # Did this file end in a new line?
                    f.seek(-1, 2)
                    ended_with_newline = f.read() == b'\n'

            except IOError as e:
                #cat: can't open 'asdfg': No such file or directory
                sys.stderr.write(f'cat: {e}\n')
