import sys

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        with open(arg, "r") as f:
            for line in f:
                print(line, end="")
