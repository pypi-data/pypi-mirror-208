import sys

from snakecan.cat   import CommandCat
from snakecan.ls    import CommandLs
from snakecan.mkdir import CommandMkdir
from snakecan.mv    import CommandMv

g_commands = {}

g_commands["cat"]    = CommandCat()
g_commands["ls"]     = CommandLs()
g_commands["mkdir"]  = CommandMkdir()
g_commands["mv"]     = CommandMv()

def main():
    cmd = g_commands[sys.argv[1]]
    cmd.parse_args(sys.argv[2:])
    cmd.run(sys.stdin, sys.stdout, sys.stderr)
