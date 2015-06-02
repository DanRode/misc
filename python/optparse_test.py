#!/usr/bin/env python

from optparse import OptionParser

def main():
    parser = OptionParser(usage="usage: %prog [options] dog|cat|fish",
                              version="%prog 1.0")
    parser.add_option('-d', '--debug', action='store_true', default=False,
                      help="Display debugging messages")
    parser.add_option('-f', '--file', 
                      action='store',
                      dest='file',
                      default='file.txt',
                      help="file to open", )
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("wrong number of arguments")

    print options
    if args[0] == "dog":
        print "got a dog"
    elif args[0] == "cat":
        print "got a cat"
    elif args[0] == "fish":
        print "got a fish"
    else:
        parser.error('"%s" not recognized' % args[0] )


if __name__ == '__main__':
    main()
