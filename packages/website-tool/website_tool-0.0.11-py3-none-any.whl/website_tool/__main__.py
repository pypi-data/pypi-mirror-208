#!/bin/env python3
from .check import check, Result, ConnectionEstablished, ConnectionEstablished
import sys
import argparse
import json


def check_parser(parser):
    parser.add_argument("roots",
                        type=str,
                        default="-",
                        help="File containing a newline-separated list of URIs to check. - for stdin")
    parser.add_argument("-p",
                        "--processes",
                        "-j",
                        type=int,
                        default=1,
                        help="Number of processes to run in parallel")

    def run(args):
        roots = sys.stdin if args.roots == "-" else open(args.roots)
        roots = roots.read().strip().split("\n")

        print(f"Checking {len(roots)} roots", file=sys.stderr)
        results = check(roots, processes=args.processes)

        json.dump(results, sys.stdout)

    parser.set_defaults(func=run)

def main():
    parser = argparse.ArgumentParser(prog="maintain-website-tool")
    parser.set_defaults(func=lambda args: parser.print_usage())

    subparsers = parser.add_subparsers()

    check_parser(subparsers.add_parser("check"))

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
