#! /usr/bin/env python
# Takes 2 filenames as input and outputs lines that only appear in each file

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("file1")
parser.add_argument("file2")
args = parser.parse_args()


def returnNotMatches(a, b):
    return [[x for x in a if x not in b], [x for x in b if x not in a]]


def main():
  with open(args.file1) as f:
    lines1 = f.readlines()

  with open(args.file2) as f:
    lines2 = f.readlines()

  uniquelines1, uniquelines2 = returnNotMatches(lines1, lines2)

  print ("======================================================")
  print ("Only in File 1")
  print ("======================================================")
  for i in uniquelines1:
    print(i.rstrip())
  print ("======================================================")
  print ("Only in File 2")
  print ("======================================================")

  for i in uniquelines2:
    print(i.rstrip())


if __name__ == '__main__':
    main()
