"""Main module definition."""

import argparse

from cynthia.tools.interpreter.interpreter import Interpreter
from cynthia.tools.shell import run_shell


def main():
    """Run shell or interpret input file."""
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?', type=argparse.FileType('r'), default=None)
    args = parser.parse_args()

    if args.file is None:
        run_shell()
    else:
        interpreter = Interpreter()
        try:
            interpreter.interpret(args.file)
        except Exception as exc:
            print(exc)


if __name__ == '__main__':
    main()
