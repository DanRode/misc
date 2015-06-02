#!/usr/bin/env python
#
# This script outputs a list of all cfwildcard groups and for each
# group lists the hostname and IP address of each member host
#

from  subprocess import *
import socket

def list_wildcard_groups():
    """Return the list of wildcard groups"""
    p = Popen(["cfwildcard-update.py", "getgroups"], stdout=PIPE)
    cmd_out = p.communicate()[0].strip()
    return cmd_out.split("\n")

def expand_wildcards(groups):
    """Expand wildcard groups and print out the expanded list for each 
       group that has members with valid IP addresses"""
    dict = {}
    for group in groups:
        p = Popen(["cfwildcard", "list", group], stdout=PIPE)
        hosts = p.communicate()[0].split()
        if hosts:
            l_ref = dict.setdefault(group, [])
            for host in hosts:
                try:
                    ip = socket.gethostbyname(host)
                    l_ref.append(host+":"+ip)
                except:
                    pass
    return dict


groups = list_wildcard_groups()
exp_wc = expand_wildcards(groups)

for key in exp_wc.keys():
    if exp_wc[key]:
        print key,
        for host in exp_wc[key]:
            print host,
        print
