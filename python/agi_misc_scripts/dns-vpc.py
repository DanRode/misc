#!/usr/bin/env python
"""
Usage: ec2mgr command [INSTANCE_ID | --fqdn FQDN]

Manages EC2 Instances

See ec2mgr --help
"""

# $Id:$

import os
import sys
sys.path.append(os.path.dirname(sys.argv[0])+"/lib/python")

import optparse
from webops import botoplus
import time
from datetime import datetime
from ConfigParser import ConfigParser
import text_table
import boto.ec2
from boto.exception import EC2ResponseError
from boto.route53 import Route53Connection
from boto.route53.record import ResourceRecordSets
from boto.route53.exception import DNSServerError
import subprocess
import pprint


class UserError(Exception):
    """Base for errors that are thrown back to invoker w/o traceback"""
    
    def __init__(self, msg):
        self.msg = msg

# options from command line
options = object


def main(argv):
    """Run command line"""
    global options
    pp = pprint.PrettyPrinter(indent=2)

    arg0 = argv[0]
    opts = {}

    parser = optparse.OptionParser()
    botoplus.add_options(parser)
    options, args = parser.parse_args(argv[1:])
    conn = botoplus.AWSConnection(options)

    if len(argv) > 1:
        instance_id = argv[1] 
        inst_by_id = conn.get_instances(instance_ids=instance_id)
        for iid, instance in inst_by_id.items():
            delete_a_records(conn, instance)
        exit(0)
    else:
        raise UserError("No Instance ID given")


def delete_a_records(conn, instance):
    """Remove DNS entries for an instance and it's aliases. 
    Takes an instance id and deletes all route 53 records
    that match that IP address."""
    instance.update()
    for zone in conn.get_all_r53_zones():
        if zone.name == "aws.imgag.com.":
            zone_records = zone.get_all_records()
            for r in zone_records:
                if r.type == "A" and \
                    r.resource_records[0] == instance.private_ip_address:
                    delete_a_record(conn, r.name, r.resource_records[0])


def delete_a_record(conn, fqdn, realname):
    """Remove a CNAME entry from route 53

    Just adds some error handling to the botoplus delete_cname
    """
    debug("deleting dns entry: "+fqdn)
    try:
	conn.delete_a_record(fqdn, realname)
    except DNSServerError as e:
        print e.error_message


def manage_ec2(command, instance_id):
    global options
    conn = botoplus.AWSConnection(options)
    delete_a_record(conn, "aws-prep7.us-east-1b.aws.imgag.com")
    exit(0)
    
    #find instance by instance ID
    try: 
        inst_by_id = conn.get_instances(instance_ids=[instance_id])
    except:
        raise UserError('Unable to find instance with ID: "%s"' % instance_id)
    # Should have exactly one entry in inst_by_id - get its value
    for iid, instance in inst_by_id.items():
        pass

    debug("Found instance: %s" % instance)

    if command=='add':
        ec2_reboot(instance)
    elif command=='delete':
        ec2_resize(conn, instance)
    elif command=='list':
        ec2_start(conn, instance)
    else:
        raise UserError("Invalid command.")


def ec2_stop(conn, instance):
    if has_elastic_ip(instance):
        if options.force:
            instance.add_tag('saved_elastic_ip', instance.ip_address)
            debug("Tagging with saved_elastic_ip: %s" % instance.ip_address)
        else:
            raise UserError("This instance has an Elastic IP. Use '--force' to stop anyway. DNS will need manual modification.")

    try:
	delete_cnames(conn, instance)
        instance.stop()
        wait_for_status(instance, "stopped")
    except EC2ResponseError as e:
        raise UserError(e.error_message)


def ec2_terminate(conn, instance):
    if has_elastic_ip(instance):
        raise UserError("This instance has an Elastic IP. Use '--force' to terminate anyway. DNS will need manual modification.")
    try:
        hostname = instance.tags.get('hostname')
	delete_cnames(conn, instance)
	delete_a_records(conn, instance)
        instance.terminate()
        wait_for_status(instance, "terminated")

        try:
            instance.add_tag('former-fqdn',instance.tags['fqdn'])
            instance.remove_tag('fqdn')
        except:
            print "Couldn't find / remove 'fqdn' tag"

        if hostname:
            # Instance had a tagged hostname.

            # Look up the cf inventory name for this host
            p = subprocess.Popen(["cfhostname", hostname],
                    stdout=subprocess.PIPE)
            cfhostname = p.communicate()[0].strip()

            if "+" in cfhostname:
                # This is a wilcard host. Remove it from wildcard group.
                subprocess.call(["cfwildcard", "del", hostname])

    except EC2ResponseError as e:
        raise UserError(e.error_message)


def get_aliases(host):
    """Find any host aliases from the cfbuild alias service"""
    global options
    alias_file = options.alias_file
    aliases = ()
    if os.path.exists(alias_file):
	debug("reading alias file: "+alias_file)
	ttparser = text_table.TextTableParser()
	for d in ttparser.parse_file(alias_file):
	    if d["name"] == host:
		# This record is for this host
		debug("found alias entry for "+host)
		for key, val in d.items():
		    aliases = d["alias"].split(",")
		break
    return aliases


def add_cnames(conn, instance):
    """Add all DNS entries for an instance"""
    instance.update()
    realname = instance.public_dns_name
    if instance.tags.has_key('fqdn'):
	add_cname(conn, instance.tags['fqdn'], realname)
    if instance.tags.has_key('hostname'):
	for alias in get_aliases(instance.tags['hostname']):
	    add_cname(conn, alias, realname)


def add_cname(conn, fqdn, realname):
    """Add a single CNAME to route 53

    Just adds some error handling to the botoplus add_cname
    """

    debug("adding entry to dns: "+fqdn)
    try:
	conn.add_cname(fqdn, realname)
    except DNSServerError as e:
            print "Warning: %s" % e.error_message


def delete_cnames(conn, instance):
    """Remove all DNS entries for an instance"""
    instance.update()
    realname = instance.public_dns_name
    if instance.tags.has_key('fqdn'):
	delete_cname(conn, instance.tags['fqdn'], realname)
    if instance.tags.has_key('hostname'):
	for alias in get_aliases(instance.tags['hostname']):
	    delete_cname(conn, alias, realname)


def delete_cname(conn, fqdn, realname):
    """Remove a CNAME entry from route 53

    Just adds some error handling to the botoplus delete_cname
    """
    debug("deleting dns entry: "+fqdn)
    try:
	conn.delete_cname(fqdn, realname)
    except DNSServerError as e:
        print e.error_message


def has_elastic_ip(instance):
    instance.update()
    elastic_ips = []
    for eip in instance.connection.get_all_addresses():
        elastic_ips.append(eip.public_ip)

    if instance.ip_address in elastic_ips:
        return True
    else:
        return False


def wait_for_status(instance, status):
    """Wait for instance to be in the specified status"""
    while True:
        if (instance.state == status):
            break
        else:
            debug('Instance state: %s' % instance.state)
            time.sleep(5)
            instance.update()
    print instance.state


def debug(str):
    """Display message if we are debugging (otherwise do nothing)"""
    global options
    if options.__dict__.get("debug"):
        print str

if __name__ == '__main__':
    retcode = 0
    try:
        main(sys.argv)
    except (UserError) as e:
        retcode = 1
        print "Error: %s" % e.msg
    except (KeyboardInterrupt):
        retcode = 1
    sys.exit(retcode)
