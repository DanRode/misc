#!/usr/bin/env python
import sys, os, optparse, re, glob, shutil
from subprocess import Popen, PIPE, STDOUT, call, check_call
file = open('repos.cfg', 'r')
repos = file.readlines()

root_dir = os.getcwd()
tmp = "%s/%s" % (root_dir, "tmp")
if not os.path.exists(tmp):
    os.makedirs(tmp)
os.chdir(tmp)
root_dir = os.getcwd()

for line in repos:
    li = line.strip()
    if not li.startswith("#"):
        os.chdir(root_dir)
        svn, git = line.split('::', 1)
        match = re.search(r'^(.+)/([^/]+)$', svn)
        repo_name = match.group(2)
        print "svn repo name %s" % repo_name
        #call(["svn", "co", "--depth=empty", svn])
        call(["svn", "co", svn])
        os.chdir(repo_name)
        
        call(["rm", "-rf", ".svn"])
        call(["git", "init"])
        call(["git", "add", "."])
        call(["git", "commit", "-m", "'Initial commit from subversion'"])

        #call(["git", "remote", "add", "origin", git])
        #call(["git", "push", "-u", "origin", "--all"])

        #os.chdir(root_dir)
        #call(["rm", "-rf", repo_name])

