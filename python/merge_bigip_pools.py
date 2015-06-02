#!/usr/bin/env python
import pprint
pp = pprint.PrettyPrinter(indent=2)
from  subprocess import *
import os

debug = 0
dc3_config = "/srv/cfmasters/site0/stable/bigip/config-dc3-1.tcl"
aws_config = "/srv/cfmasters/site-aws/stable/bigip/config-dc3-1.tcl"

outfile = "bigip-cfg-combined.tcl"
bigip_hostname = "dc3-bigip1"
aws_cf_hostname = "cf-a1.us-east-1a.aws.imgag.com"


def parse_dc3_config(file, aws_pools):
    "Read config file and create a dictionary of settings"
    cfg = []
    lines = filter(None, [line.rstrip() for line in open(file)])
    for line in lines:
        if line.startswith("pool"):
            pool = line.split()[1]

        if line.startswith("}"):
            if pool in aws_pools:
                for aws_member in aws_pools[pool]:
                    cfg.append("   %s" % aws_member)
                del aws_pools[pool]
            cfg.append(line)
        else:
            cfg.append(line)

    if len(aws_pools) != 0:
        print
        print "ERROR: Invalid AWS pool"
        print "\n".join(aws_pools)
        print
        exit(1)
    return cfg

def parse_aws_config(file):
    "Read config file and create a dictionary of settings"
    cfg = {}
    lines = filter(None, [line.strip() for line in open(file)])
    for line in lines:
        if line.startswith("pool"):
            pool = line.split()[1]
        elif line.startswith("member"):
            member = line.split()[1]
            x = cfg.setdefault(pool, [])
            if member not in x:
                x.append(member)
    return cfg

def expand_wildcards(pool_dict):
    """Expand wildcard members and update members list"""
    wc_groups = {}
    ip_cache = {}
    pools = {}
    expand_cmd = ["ssh", "-A", 
            "root@" + aws_cf_hostname, 
            "expand_wildcard_groups.py",]
    if debug:
        expand_cmd = ["cat", "/home/drode/expand_wildcard_groups.out",]
    p = Popen(expand_cmd, stdout=PIPE)
    lines = p.communicate()[0].strip()
    lines = lines.split("\n")
    if debug:
        for line in lines:
            print "LINE: %s" % line
        print "END LINES"
    for line in lines:
        grp_list = line.split()
        hosts = wc_groups.setdefault(grp_list[0], [])
        for host in grp_list[1:]:
            hosts.append(host.split(":")[1])

    for pool, members in aws_members.items():
        member_list = pools.setdefault(pool, [])
        for member in members:
            host, port = member.split(':')
            if host.endswith('+'):
                if host in wc_groups:
                    wc_members = wc_groups[host]
                    for wc_member in wc_members:
                        member_list.append("member %s:%s" % (wc_member,port))
            else:
                if host not in ip_cache:
                    lookup_cmd = ["ssh", "-A", 
                            "root@" + aws_cf_hostname, 
                            "host", host,]
                    p = Popen(lookup_cmd, stdout=PIPE)
                    line = p.communicate()[0].split()
                    ip_cache[host] = line[3]
                std_member = ip_cache[host]
                member_list.append("member %s:%s" % (std_member,port))
    return pools

print "Reading AWS and DC3 BigIP pools"
aws_members = parse_aws_config(aws_config)
expanded_list = expand_wildcards(aws_members)
config = parse_dc3_config(dc3_config, expanded_list)
print "Creating merged config file: %s" % outfile
o = open(outfile, 'w')
o.write("\n".join(config))

scp_cmd = "scp -q %s %s:" % (outfile, bigip_hostname)
ret_code = os.system(scp_cmd)
if ret_code != 0:
    print "ERROR: scp of %s to %s failed" % (outfile, bigip_hostname)
else:
    print "Copying config file to %s" % (bigip_hostname)
