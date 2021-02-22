import os
import sys

if __name__ == "__main__":
    os.environ[sys.argv[1]] = sys.argv[2]
    sys.exit(0)
