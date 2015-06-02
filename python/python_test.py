#!/usr/bin/env python2.6
import argparse
class argPrint(object):

    def __init__(self, arga, argb):
        """Method docstring"""
        self.arg1 = arga
        self.arg2 = argb

    def printargs(self):
        """printarge method docstring"""
        print self.arg1
        print self.arg2

#instance = argPrint('arg1a', 'arg2b')
#print type(instance)
#instance.printargs()

#print dir(instance)

class dogs:
    legs = 0
    color = None
    name = None
    def printDog(self):
        print "Name: %s" % self.name
        print "Legs: %s" % self.legs
        print "Color: %s" % self.color


parser = argparse.ArgumentParser(description='Python test app with classes')
parser.add_argument('-n','--name', help='Name of dog', required=True)
parser.add_argument('-c','--color', help='Color of dog', required=True)
parser.add_argument('-l','--legs', help='Number of legs', default=4)
args = vars(parser.parse_args())

dog = dogs()
dog.legs = args['legs']
dog.name = args['name']
dog.color = args['color']
dog.printDog()

li = ['a', 'b', 'test', 'drode', 'misc',]


