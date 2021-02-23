import argparse as ap

import regex as re

argparser = ap.ArgumentParser()
argparser.add_argument(
    "pattern",
    metavar="PATTERN",
    type=str,
    help="pattern that will be searched for",
)
argparser.add_argument(
    "files",
    metavar="FILE",
    type=str,
    nargs="+",
    help="files where the pattern will be searched for",
)
argparser.add_argument(
    "-i",
    dest="insensitive",
    action="store_true",
    help="case insensitive search",
)
argparser.add_argument(
    "-w",
    dest="literal",
    action="store_true",
    help="pattern is search for literally",
)
argparser.add_argument(
    "-A",
    dest="after",
    type=int,
    default=0,
    help="number of lines to print following the match",
)


if __name__ == "__main__":
    args = argparser.parse_args()

    flags = 0
    pat = args.pattern
    if args.insensitive:
        flags |= re.IGNORECASE
    if args.literal:
        pat = re.escape(pat)
    pattern = re.compile(pat, flags)

    for phyle in args.files:
        with open(phyle, "r") as f:
            context = 0
            for line in f:
                if pattern.search(line):
                    context = args.after + 1
                if context != 0:
                    print(line, end="")
                    context -= 1
