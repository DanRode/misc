#!/usr/bin/env python

from  subprocess import *

dc3_config = "/home/drode/svn/rel/site0/bigip/config-dc3-1.tcl"
aws_config = "/home/drode/svn/rel/site-aws/bigip/config-dc3-1.tcl"


def parse_aws_config(file):
    "Read config file and create a global dictionary of settings"
    cfg = {}

    lines = filter(None, [line.strip() for line in open(file)])

    for line in lines:
        if line.startswith("pool"):
            pool = line.split()[1]
        elif line.startswith("member"):
            member = line.split()[1]
            x  = cfg.setdefault(pool, [])
            if member not in x:
                x.append(member)


    return cfg

def expand_wildcards(pool_dict):
    """Expand wildcard members and update members list"""
    for pool, members in aws_members.items():
        for member in members:
            host, port = member.split(':')
            if host.endswith('+'):
                print "WILDCARD " + host
                ### This has to run in AWS ###
                p = Popen(["cfwildcard", "list", host], stdout=PIPE)
                hosts = p.communicate()[0].strip()
                xxx = hosts.split("\n")
                print "HOSTS: "
                for x in xxx:
                    print "X: " + x

            else:
                print "STD HOST " + host

xxx = """
pool api-varnish {
   lb method member least conn
   monitor all tcp
   member 172.30.220.162:http
   member 172.30.220.163:http
   member 172.30.220.164:http

pool stg1-sff {
   lb method member least conn
   monitor all local_http_checktxt2
   member stg-web-a+:54080
   member stg-web-a1:54080
}
"""

aws_members = parse_aws_config(aws_config)
expand_wildcards(aws_members)
#aws_members = parse_aws_config(dc3_config)
#print aws_members


#for pool, members in aws_members.items():
#    print pool
#    for member in members:
#        print "   " + member

