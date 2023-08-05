from functools import lru_cache
import argparse

@lru_cache(maxsize=None)
def unique(word):
    if type(word) == str:
        c = 0
        s = {}
        for i in word:
            s[i] = word.count(i)
        return len([i for i, j in s.items() if j == 1])
    else:
        return 'TypeError'

def addarg():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', nargs=1)
    parser.add_argument('--string', nargs=1)
    args = parser.parse_args()


def checkargs(args):
    if args.file and args.file[0] and not args.string:
        with open(args.file[0], 'r') as filee:
            print(unique(str(filee.readline())))
    if args.string and args.string[0] and not args.file:
        print(unique(args.string[0]))
    if args.file and args.string and args.file[0] and args.string[0]:
        with open(args.file[0], 'r') as filee:
            print(unique(str(filee.readline())))
        print(unique(args.string[0]))