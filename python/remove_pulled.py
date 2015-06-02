#!/usr/bin/env python
#
import sys, os, optparse, re, glob, shutil
import pprint
from subprocess import Popen, PIPE, STDOUT, call, check_call

pp = pprint.PrettyPrinter(indent=2)
asset_file = "/home/drode/svn/top/asset.txt"
pulled_file = "/home/drode/svn/top/pulled.txt"

new_pulled = []
tags = []
pulled  = filter(None, [line.strip() for line in open(pulled_file)])
for pline in pulled:
    try:
        k, v = str.split(pline, None, 1)
        if k[0].isdigit() and k[1].isdigit():
            tags.append(k)
    except:
        continue

new_assets = []
assets  = filter(None, [line.strip() for line in open(asset_file)])
for aline in assets:
    if aline.startswith("#"):
        new_assets.append(aline)
    else:
        k, v = str.split(aline, None, 1)
        if k in tags:
            print "Found %s in pulled.txt removing from asset.txt" % k
            new_pulled.append(aline)
        else:
            new_assets.append(aline)

print "Moving %s matches from assets.txt to pulled.txt" % len(new_pulled)

print "Writing out new_assets.txt"
na =  open('/home/drode/new_assets.txt', 'w')
for line in new_assets:
    na.write(line + "\n")
na.close()

print "Writing out list removed assets"
pa =  open('/home/drode/new_pulled.txt', 'w')
#for line in pulled:
#    pa.write(line + "\n")
for line in new_pulled:
    pa.write(line + "\n")
pa.close()

exit(0)
ra =  open('/home/drode/retired_detail.txt', 'w')
for host in tags:
    p = Popen(('fh ' + host), shell=True, stdout=PIPE).stdout
    plines = filter(None, [pline.strip() for pline in p.readlines()])
    for line in plines:
        ra.write(line + "\n")
    ra.write("\n")
pa.close()

