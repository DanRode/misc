#!/usr/bin/env python

class svnCheckout:
    # Attributes (properties)
    syspath = "System path to svn checkout"
    svnpath = "Svn path"
    checkout = ""
    directory = ""


    # methods
    def isCheckout(self, x):
        do stuff to ifnd out if this is already a valod svn checkout

    def isDirectory(self, x):
        self.age = x
    def 

    def talk(self):
        #print "Hi! My name is %s and I am %s" % (self.name, self.age)
        print "Hi! My name is", self.name, "and I am", self.age



name = raw_input('Name: ')
age = raw_input('Age: ')
p = Person()
p.setAge(age)
p.setName(name)

p.talk()
