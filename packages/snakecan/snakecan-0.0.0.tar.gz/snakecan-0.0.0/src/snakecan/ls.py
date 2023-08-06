import argparse
import os
import math
import stat
import pathlib
import sys
from typing import Union

from snakecan import util
from snakecan.basecommand import BaseCommand


def sort_entry_name(entry: dict):
    return entry['name_raw']

def sort_entry_size(entry: dict):
    class SortData:
        def __init__(self, entry: dict):
            self.name = entry['name_raw']
            self.size = entry['size']
        def __lt__ (self, other):
            if self.size == other.size:
                return self.name < other.name
            return self.size > other.size
    return SortData(entry)

def sort_entry_mtime(entry: dict):
    class SortData:
        def __init__(self, entry: dict):
            self.name = entry['name_raw']
            self.mtime = entry['mtime']
        def __lt__ (self, other):
            if self.mtime == other.mtime:
                return self.name < other.name
            return self.mtime > other.mtime
    return SortData(entry)

class CommandLs(BaseCommand):
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('paths', nargs='*')

        self.parser.add_argument('-a', '--all', action='store_true')
        self.parser.add_argument('-A', '--almost-all', action='store_true')
        self.parser.add_argument('-r', '--reverse', action='store_true')

        self.parser.add_argument('--sort', choices=['none', 'name', 'size', 'time'], default='name')
        self.parser.add_argument('--hyperlink', choices=['always', 'auto', 'never'], default='auto')
        self.parser.add_argument('--color', choices=['always', 'auto', 'never'], default='auto')
        self.parser.add_argument('--format', choices=['verbose', 'long', 'commas', 'horizontal', 'across', 'vertical', 'single-column', 'auto'], default='auto')
        
        self.parser.add_argument('-1', action='store_const', const='single-column', dest='format')
        self.parser.add_argument('-C', action='store_const', const='horizontal', dest='format')

        self.parser.add_argument('-S', action='store_const', const='size', dest='sort')
        self.parser.add_argument('-t', action='store_const', const='time', dest='sort')

    def parse_args(self, args):
        self.args = self.parser.parse_args(args)

        # If no paths were specified, use the CWD
        if len(self.args.paths) == 0:
            self.args.paths = ['.']

        # Passing all implies almost all
        if self.args.all:
            self.args.almost_all = True

        # Convert hyperlink into a bool
        if self.args.hyperlink == 'auto':
            # Auto means we need to check if we're in a tty
            self.args.hyperlink = sys.stdout.isatty()
        elif self.args.hyperlink == 'always':
            self.args.hyperlink = True
        else:
            self.args.hyperlink = False

        # Convert color into a bool
        if self.args.color == 'auto':
            # Auto means we need to check if we're in a tty
            self.args.color = sys.stdout.isatty()
        elif self.args.color == 'always':
            self.args.color = True
        else:
            self.args.color = False

        # Cleanup format
        if self.args.format == 'auto':
            # Auto means we need to check if we're in a tty
            self.args.format = 'vertical' if sys.stdout.isatty() else 'single-column'
        elif self.args.format == 'long':
            self.args.format = 'verbose'
        elif self.args.format == 'across':
            self.args.format = 'horizontal'
        

    def format_entry(self, entry: Union[os.DirEntry,pathlib.Path]):
        name = entry.name
        entry_path = pathlib.Path(entry.path) if isinstance(entry, os.DirEntry) else entry 

        # If the name is empty, it's the current directory
        if len(name) == 0:
            name = '.'
        
        # Make it a hyperlink!
        if self.args.hyperlink:
            name = util.vt_hyperlink(name, 'file://' + str(entry_path.absolute()))

        # Color the text!
        if self.args.color:
            # Format the name
            if entry.is_symlink():
                # Symlinks
                name = util.vt_color(name, foreground=util.VTColor.CYAN)
            elif entry.is_dir():
                # Directories
                name = util.vt_color(name, foreground=util.VTColor.BLUE)
            else:
                # Executables
                exec = False

                # If we're on Windows, executable files are any .exe or .bat
                if util.plat_is_windows():
                    ext = entry_path.suffix.lower()
                    if ext == '.exe' or ext == '.bat':
                        exec = True
                else:
                    # On most other platforms, we can just check if it's executable
                    mode = entry.stat().st_mode
                    if (stat.S_IXUSR & mode) or (stat.S_IXGRP & mode) or (stat.S_IXOTH & mode):
                        exec = True

                # Mark executables green
                if exec:
                    name = util.vt_color(name, foreground=util.VTColor.GREEN)

        return name
        
    def run(self, stdin, stdout, stderr):

        reverse_sort = False
        sort_func = sort_entry_name
        if self.args.sort == 'size':
            sort_func = sort_entry_size
        elif self.args.sort == 'time':
            sort_func = sort_entry_mtime

        reverse_sort = reverse_sort != self.args.reverse

        for path in self.args.paths:
            with os.scandir(path) as entries_raw:

                # Create a sorted list of formatted names and a bit of extra data for all entries
                entryinfos = []
                max_entry_len = 0
                for entry in entries_raw:
                    
                    # If not using -A or -a, ignore filenames that begin with .
                    if not self.args.almost_all and entry.name[0] == '.':
                        continue
                    
                    # Keep track of the longest name
                    max_entry_len = max(max_entry_len, len(entry.name))
                    
                    # Get stat info for sorting
                    entry_stat = entry.stat()

                    # Track the entry!
                    e = dict(
                        name_raw = entry.name,
                        name = self.format_entry(entry),
                        mtime = entry_stat.st_mtime,
                        size = entry_stat.st_size
                    )
                    entryinfos.append(e)

                # If we're using -a, add in the current directory . and the parent directory ..
                if self.args.all:
                    # Current directory
                    entry_stat = os.stat('.')
                    e = dict(
                        name_raw = '.',
                        name = self.format_entry(pathlib.Path('.')),
                        mtime = entry_stat.st_mtime,
                        size = entry_stat.st_size
                    )
                    entryinfos.append(e)
                    
                    # Parent directory
                    entry_stat = os.stat('..')
                    e = dict(
                        name_raw = '..',
                        name = self.format_entry(pathlib.Path('..')),
                        mtime = entry_stat.st_mtime,
                        size = entry_stat.st_size
                    )
                    entryinfos.append(e)

                # Sort the list so we can print it correctly!
                entryinfos.sort(key = sort_func, reverse=reverse_sort)

                match self.args.format:

                    case 'single-column':
                        # Single column formatting does not need any special layouting
                        for entry in entryinfos:
                            stdout.write(entry['name'])
                            stdout.write('\n')

                    case 'commas':
                        # Single column formatting does not need any special layouting
                        for entry in entryinfos[:-1]:
                            stdout.write(entry['name'])
                            stdout.write(', ')
                        stdout.write(entryinfos[-1]['name'])
                        stdout.write('\n')

                    case 'horizontal' | 'vertical':                        
                        # How should we handle spacing?
                        column_width = max_entry_len + 2
                        term_width = os.get_terminal_size().columns if stdout.isatty() else 160
                        num_cols = math.floor(term_width / column_width)
                        num_rows = math.ceil(len(entryinfos) / num_cols)
                        
                        # Print entries as a table
                        for row in range(num_rows):
                            for col in range(num_cols):
                                # Get the entry, but don't access out of bounds!
                                if self.args.format == "vertical":
                                    i = col * num_rows + row
                                else:
                                    i = row * num_cols + col
                                if i >= len(entryinfos):
                                    break
                                entryinfo = entryinfos[i]

                                # Pad the name
                                name = entryinfo['name'] + (' ' * (column_width - len(entryinfo['name_raw'])))
                                stdout.write(name)
                            stdout.write('\n')



