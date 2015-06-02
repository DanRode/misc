#!/usr/bin/env python
#
import sys, os, optparse, re, glob, shutil
import pprint
from subprocess import Popen, PIPE, STDOUT, call, check_call

pp = pprint.PrettyPrinter(indent=2)
rec_dict = {}
tags_file = "/home/drode/recycle-01-2014/scanned_assets.txt"
asset_file    = "/home/drode/svn/top/asset.txt"
pulled_file   = "/home/drode/svn/top/pulled.txt"

found_tags = []
new_assets = []
new_pulled = []

tags = filter(None, [line.strip() for line in open(tags_file)])
assets   = filter(None, [line.strip() for line in open(asset_file)])
pulled   = filter(None, [line.strip() for line in open(pulled_file)])
j = 0
i = 0

# Read in asset.txt looking for matching asset tags to remove
for aline in assets:
    if aline.startswith("#"):
        new_assets.append(aline)
    else:
        k, v = str.split(aline, None, 1)
        if k in tags:
            new_pulled.append(aline)
            found_tags.append(k)
            j += 1

        else:
            new_assets.append(aline)

print j
print "Moving %s matches from assets.txt to pulled.txt" % len(new_pulled)

na =  open('/home/drode/recycle-01-2014/new_assets.txt', 'w')
for line in new_assets:
    na.write(line + "\n")
na.close()

pa =  open('/home/drode/recycle-01-2014/new_pulled.txt', 'w')
for line in pulled:
    pa.write(line + "\n")
for line in new_pulled:
    pa.write(line + "\n")
pa.close()

print "new_asset.txt and new_pulled.txt created"
print " "
for x in tags:
    if x not in found_tags:
        print "Not found: %s" % x

exit(0)
print "Creating detail file for each host"

ra =  open('/home/drode/recycle-01-2014/retired_detail.txt', 'w')
for host in tags:
    p = Popen(('fh ' + host), shell=True, stdout=PIPE).stdout
    plines = filter(None, [pline.strip() for pline in p.readlines()])
    for line in plines:
        ra.write(line + "\n")
    ra.write("\n")
pa.close()

