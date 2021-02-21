import fileinput
import sys

if __name__ == "__main__":
    for line in fileinput.input():
        print(line, end="")
