#!/usr/bin/env python
import sys, os, optparse, re, glob, shutil
from subprocess import Popen, PIPE, STDOUT, call, check_call
headerRow = ["Path", "Working Copy Root Path", "URL", "Relative URL", "Repository Root", "Repository UUID", "Revision", "Node Kind", "Schedule", "Last Changed Author", "Last Changed Rev", "Last Changed Date",]
def get_svn_info(svnpath):
    p = Popen( ('/usr/bin/svn info ' + svnpath), shell=True, stdout=PIPE).stdout
    plines = filter(None, [pline.strip() for pline in p.readlines()])
    plist = [re.sub(r'^.*?: ', '', pline) for pline in plines]

    print(','.join(plist))
    #print(', '.join('"{0}"'.format(w) for w in plist))


args = sys.argv[1:]
print(','.join(headerRow))
for repo in args:
    get_svn_info(repo)
