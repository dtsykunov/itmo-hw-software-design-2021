import sys

if __name__ == "__main__":
    with open(sys.argv[1], "r") as f:
        lines, words, byts = 0, 0, 0
        for line in f:
            lines += 1
            words += len(lines.split(' '))
            byts = len(line)
        print(lines, words, byts)
