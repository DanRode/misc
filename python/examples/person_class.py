#!/usr/bin/env python

class Person:
    # Attributes (properties)
    name = "No name yet"
    age = 0

    # methods
    def setName(self, x):
        self.name = x

    def setAge(self, x):
        self.age = x

    def talk(self):
        #print "Hi! My name is %s and I am %s" % (self.name, self.age)
        print "Hi! My name is", self.name, "and I am", self.age



name = raw_input('Name: ')
age = raw_input('Age: ')
p = Person()
p.setAge(age)
p.setName(name)

p.talk()
