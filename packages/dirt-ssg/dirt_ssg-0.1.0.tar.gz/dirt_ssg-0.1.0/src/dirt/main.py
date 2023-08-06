"""dirt: a dirt simple static site generator
Command line main to run dirt from the shell.
Includes a secret command line --profile to run profiler.
See README.md

Command line:
python3 main.py -h
"""


__author__ = "Loren Kohnfelder"
__copyright__ = "Copyright 2022 Loren Kohnfelder"
__version__ = "0"
__license__ = "CC BY-SA 4.0"


from dirt.common import META_DIR, DIRT_TOML

import argparse
from dirt.ssg import cli
import os
import sys


def main(argv=None):
    """Parse command line arguments and invoke processing.
    Run with --help for full options.
    """
    parser = argparse.ArgumentParser(
        description="A dirt simple static site generator",
        epilog=("Version: %s" % __version__))
    standard_meta_config = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '../..', META_DIR, DIRT_TOML)
    parser.add_argument('-c', '--config', help="root config file",
                        action='store',
                        default=standard_meta_config)
    parser.add_argument('-i', '--input', action='store',
                        help="directory of source content files",
                        default='./content/')
    parser.add_argument('-l', '--localhost', help="hostname for local server",
                        action='store',
                        default='localhost')
    parser.add_argument('-p', '--port', help="port for local server",
                        action='store', type=int,
                        default=1313)
    parser.add_argument('-n', '--noautoupdate',
                        help="prevent auto update when files change",
                        action='store_true')
    parser.add_argument('-o', '--output', action='store',
                        help="directory of generated site files",
                        default='./public/')
    parser.add_argument('-v', '--verbose', help="verbose output mode",
                        action='store_true')
    parser.add_argument('action', nargs='?', default='make',
                        choices=['start', 'make', 'server', 'check'],
                        help="Action to take (default make)")
    parser.add_argument('--profile',
                        help="run performance profile for development",
                        action='store_true')
    args = parser.parse_args(argv)
    if (args.verbose):
        print("args: " + repr(args))
    error_message = cli(args)
    if (error_message):
        print(error_message, file=sys.stderr)


if __name__ == '__main__':
    if ('--profile' in sys.argv[1:]):
        import cProfile
        main_call = "main(%s)" % repr(sys.argv[1:])
        print(main_call)
        cProfile.run(main_call)
    else:
        main(sys.argv[1:])
