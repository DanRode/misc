#!/usr/bin/env python
# $Id:$
#
# To create the input file run the find command below
# Find files in given path and then print the size in byes for each
# This will work a very large number of files
#
# find /some/path/ -type f -print0 | xargs -0 du -b 

from __future__ import division
import sys, os, re

total_size = 0
total_files =  0
detailDict = {}
filetypeDict = {}

filetypelist = [ "-inside.pdf", "-inside.xml", "-outside.pdf", "-outside.xml", "-distribution.xml", "-envelopes.xml", "-outside-300dpi.jpg", "-inside-300dpi.jpg", "jpg", "xml", "pdf" ]
dirlist = ["/fs/remote/assets/web/product/ag", "/fs/remote/assets/web/product/cardstore", "/fs/remote/assets/web/product/jw", "/fs/remote/assets/print/render"]
inputFile  = "/home/drode/fs_remote_du_2.out"
print "Searching the following paths"
for x in dirlist:
    print x

print " "
print "Reporting on the following file type matches"
for x in filetypelist:
    print x
print " "
lines = filter(None, [line.strip() for line in open(inputFile)])

for line in lines:
    size, filePath = line.split(None, 1)
    for dir in dirlist:
        if filePath.startswith(dir):
            for i in filetypelist:
                if (filePath.endswith(i)):
                    path, file = os.path.split(filePath)
                    uniqueKey = "%s-(%s)" % (dir, i)
                    detailDict.setdefault(uniqueKey, {'files': 0, 'sum': 0})['files'] += int(1)
                    detailDict.setdefault(uniqueKey, {'files': 0, 'sum': 0})['sum'] += int(size)

                    filetypeDict.setdefault(i, {'files': 0, 'sum': 0})['files'] += int(1)
                    filetypeDict.setdefault(i, {'files': 0, 'sum': 0})['sum'] += int(size)

            total_size =  total_size + int(size)
            total_files =  total_files + 1

# Print the file count, total size and average size by location (dir) and file type
# Many files will be counted twice as they will match more than one item in filetypelist
print "Files by type found each searched path"
for key in detailDict.keys():
    files = detailDict[key]['files']
    filekb = detailDict[key]['sum'] / 1024 / 1024
    fileavg = detailDict[key]['sum'] / detailDict[key]['files'] / 1024
    print "%s files %0.2f mb %0.2f kb avg %s" % (files, filekb, fileavg, key)
print " "

# Print the file count, total size and average size by file type spanning all locations
# As above, duplicates are expected
print "Files by type found in any searched path"
for key in filetypeDict.keys():
    files = filetypeDict[key]['files']
    filekb = filetypeDict[key]['sum'] / 1024 / 1024
    fileavg = filetypeDict[key]['sum'] / filetypeDict[key]['files'] / 1024
    print "%s files %0.2f mb %0.2f kb avg %s" % (files, filekb, fileavg, key)
print " "

# Print the file count, total size and average size for all files. 
# Files are only counted once; no dupicates.
print "Files of any types and searched path"
print "%s files %0.2f mb %0.2f kb avg" % (total_files, total_size / 1024 / 1024, total_size / total_files / 1024 )
print " "
