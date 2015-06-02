#!/usr/bin/env python
# $Id:$
#
#a = "val1"
import sys
import time
import os
cmd = "/usr/bin/svn"
arg1 = 'info'
ar2g = '/home/drode/content'
svncmd = "/usr/bin/svn info /home/drode/content"

p  = os.popen(svncmd, "r")
lines = filter(None, [line.strip() for line in p.readlines()])
for line in lines:
    line = line.rstrip('\r\n')

    print "line: %s" % line



#dict = {}
#val = "three"
#dict = {"one": 1, "two": 2}
#if dict.has_key(val):
    #print "%s = %s" % (val, dict[val])
#else :
    #print "%s not found" % val
