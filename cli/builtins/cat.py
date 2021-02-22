import fileinput
import sys

if __name__ == "__main__":

    # if len(sys.argv[:-1]) == 0:
    #     for line in sys.stdin:
    #         print(line)
    #     sys.exit(0)
    for line in fileinput.input():
        print(line)
    sys.exit(0)

    for arg in sys.argv[1:]:
        with open(arg, "r") as f:
            for line in f:
                print(line, end="")
