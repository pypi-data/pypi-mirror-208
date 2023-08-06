#!/usr/bin/env python

import sys
import argparse
from src.actions import install, add, init, execute_script, remove, show
from src.core import barn_action, Context

def main():

    title = r"""
_________                   
______/ /_  ____ __________ 
_____/ __ \/ __ `/ ___/ __ \
___ / /_/ / /_/ / /  / / / /
___/_.___/\__,_/_/  /_/ /_/
    """
    print(title)
    version = '.'.join(map(str, sys.version_info[:3]))
    if not version.startswith("3.9"):
        print("Barn requires Python 3.9 or higher")
        sys.exit(1)

    class IgnoreUnknownArgParser(argparse.ArgumentParser):
        def error(self, message):
            pass

    parser = IgnoreUnknownArgParser(description='Barn CLI tool', add_help=False)
    subparsers = parser.add_subparsers(dest='command')

    # Add 'install' command
    subparsers.add_parser('install')

    # Add 'add' command
    add_parser = subparsers.add_parser('add')
    add_parser.add_argument(
        "requirement",
        help="The name of package to add, versioning is also supported"
    )

    remove_parser = subparsers.add_parser('remove')
    remove_parser.add_argument("package_name", help="The name of package to add, versioning is also supported")

    show_parser = subparsers.add_parser('show')
    show_parser.add_argument("-v", "--verbose", help="extra text", action='store_true')
    show_parser.add_argument("package_name", help="The name of package to show")
    show_parser.add_argument("-f", "--files", help="Show the full list of files", action='store_true')

    # subparsers.add_parser('test')

    # Parse the arguments
 
    args, unknown_args = parser.parse_known_args()

    exit_code = 0
    if len(unknown_args) > 0 and args.command is None:
        _, exit_code = execute_script(unknown_args[0], unknown_args[1:])
    # If no command is given, print help and exit
    elif args.command is None:
        _, exit_code = install()
    elif args.command == 'show':
        _, exit_code = show(args.package_name, verbose=args.verbose, files=args.files)
    elif args.command == 'install':
        _, exit_code = install()
    elif args.command == 'remove':
        _, exit_code = remove(args.package_name)
    elif args.command == 'add':
        _, exit_code = add(args.requirement)
    elif args.command == 'init':
        init()
    elif args.command == 'test':
        @barn_action
        def test_action(context: Context=None):
            # Do whatever here
            context.add_dependency_to_project_yaml("test", "1.0.0")
        test_action()
    else:
        print("Unknown command: " + args.command)

    sys.exit(exit_code)
