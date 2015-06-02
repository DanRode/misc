# Can do the import and set trace inline as neeeded
# http://docs.python.org/2.6/library/pdb.html
import pdb 
pdb.set_trace()

# Dump all the data from an object
print some_object.__dict__

# Make the dumped data more readabl
# http://docs.python.org/2.6/library/pprint.html
import pprint
pp = pprint.PrettyPrinter(indent=2, depth=2)
pp.pprint(some_object.__dict__)
pp.pprint(some_dict_or_list_or_)

# debug logging
import logging
logging.basicConfig(filename="boto.log", level=logging.DEBUG)


##############################################################
# Example of getting CLI input and using switch
##############################################################
def function1():
    print 'You chose one.'
def  function2():
    print 'You chose two.'
def  function3():
    print 'You chose three.'
#
# switch is our dictionary of functions
switch = {
    'one': function1,
    'two': function2,
    'three': function3,
    }
#
# choice can eithe be 'one', 'two', or 'three'
choice = raw_input('Enter one, two, or three :')
#
# call one of the functions
try:
    result = switch[choice]
except KeyError:
    print 'I didn\'t understand your choice.'
else:
    result()
##############################################################

##############################################################
# Example of a simple class
##############################################################
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
##############################################################
mylist = ["first", "second", "third", "fourth",]

# Access the index while looping through a list
for idx, val in enumerate(mylist):
        print idx, val

#!/usr/bin/python
import sys
# Print the number of comamnd line args
X = len(sys.argv)
if X > 0:
    X = X - 1
    print "Number of args: ", X

# Print each argument
j=0
for i in sys.argv:
    print "arg ", j, ": ", i
    j = j + 1 # ++j is not supported

# Test for a specific argument and handle the exception
# if the variable does not exist
#try: sys.argv[1]
#except NameError:
try: myVar
except IndexError:
    # Do something if it does not exist
    # argv[0] always exists if sys is imported
    print "argv[0]:", sys.argv[0]
else:
    # Do something if it exists
    print "argv[0]:", sys.argv[0], "argv[1]: ", sys.argv[1]
# open a file and read in line by line
import string
import os
for line in os.popen(Cmd).readlines():
    # Remove trailing newline
    line = line.rstrip()
    # Skip if line begins 
    if len(line) == 0 or line.startswith('Filesystem'):
	continue
    else:
	D = line.split()
        # Convert to a float and divide by 1024 to the 3 power
	D[1] = float(D[1]) / 1024**3
# Store an array in a dictionary 
# key is array element, value is dictionary reference
# Return thre dictionay reference 
    myDict[myArray[5]] = myArray
return(myDict)

# Sort a dictionary by key, then print each item
myDict = {'apple': [1.99, "red", "tart"], 'bananna': [.59, "yellow", "bland"], 'orange': [1.79, "orange", "sour"]}
keys = myDict.keys()
keys.sort()
print "product    color    taste     price"
print "==================================="
for  key in keys:
    print "%-10s %-8s %-8s %6.2f " % (key, myDict[key][1], myDict[key][2], myDict[key][0])

