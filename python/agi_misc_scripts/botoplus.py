#!/usr/bin/env python
"""
Webops wrappers for the AWS boto library.

"""

# $Id:$

import optparse
import sys
import time
from datetime import datetime
from ConfigParser import ConfigParser
import boto.ec2
import boto.ec2.elb
import boto.sdb
from boto.route53.connection import Route53Connection
from boto.route53.record import ResourceRecordSets
from boto.iam.connection import IAMConnection
from boto.vpc import VPCConnection

_ec2_key_name = "webops"
# IAM access/secret key locations
_aws_account_number = "311514151974"
_r53_zone_id = "Z18W2UOXJIGDJ" #zone id for aws.imgag.com.

def add_options(parser):
    "Add boto options to optparse parser"
    parser.add_option('-r', '--region',
        default='us-east-1',
        help='AWS region to connect to (us-east-1)')


class R53Zone():
    """Representation of a Route 53 Zone"""
    def __init__(self, r53, boto_zone):
        self._r53 = r53
        self.id = boto_zone['Id'].replace('/hostedzone/', '')
        self.name = boto_zone['Name']
        try:
            self.comment = boto_zone['Config']['Comment']
        except KeyError:
            self.comment = ""

    def __repr__(self):
        return "id=%s, name=%s, comment=%s" % (self.id, self.name, self.comment)

    def get_all_records(self, type=None, name=None, identifier=None,
                       maxitems=None):
        """Retrieve the Resource Record Sets defined for this Hosted Zone."""
        return self._r53.get_all_rrsets(self.id, type, name,
                                        identifier, maxitems)


class AWSConnection(object):
    def __init__(self, options, region=None, **connect_args):
	self._ec2 = None
	self._vpc = None
	self._elb = None
	self._s3 = None
	self._r53 = None
	self._region = region or options.region
	self._connect_args = connect_args

    def get_ec2(self):
	if self._ec2 is None:
	    cargs = self._connect_args
	    region = boto.ec2.get_region(self._region, **cargs)
	    self._ec2 = region.connect(**cargs)
	return self._ec2

    def get_vpc(self):
	if self._vpc is None:
	    cargs = self._connect_args
            self._vpc = VPCConnection(**cargs)
	return self._vpc

    def get_elb(self):
	if self._elb is None:
	    cargs = self._connect_args
	    self._elb = boto.ec2.elb.connect_to_region(self._region, **cargs)
	return self._elb

    def get_s3(self):
	if self._s3 is None:
	    cargs = self._connect_args
	    self._s3 = boto.connect_s3(**cargs)
	return self._s3

    def get_bucket(self, name, **kwargs):
	return self.get_s3().get_bucket(name, **kwargs)

    def get_instances(self, instance_ids=None, filters=None):
	"""Get dictionary of instance info indexed by iid"""
	inst_by_id = {}
	ec2 = self.get_ec2()
	for reservation in ec2.get_all_instances(
		instance_ids=instance_ids,
		filters=filters,
		):
	    for instance in reservation.instances:
		inst_by_id[instance.id] = instance
	return inst_by_id

    def find_instance_for(self, fqdn, cache=False):
        """Find the instance object associated with the given fqdn."""
        if not fqdn.endswith('.'):
            fqdn = "%s." % fqdn
        if cache:
	    if not self.__dict__.has_key("_instances"):
                self._instances = self.get_instances()
            instances = self._instances
        else:
            instances = self.get_instances()
        for id, instance in instances.iteritems():
            if instance.state == "terminated":
                continue
            if instance.__dict__['tags'].get('fqdn') == fqdn:
                return instance
        return None

    def get_my_images(self, filters=None):
	"""Get list of AMI images owned by us"""
	ec2 = self.get_ec2()
	return ec2.get_all_images(owners=_aws_account_number,
		filters=filters)

    def get_load_balancers(self, lbnames=None):
	return self.get_elb().get_all_load_balancers(lbnames)

    def get_r53(self):
	if self._r53 is None:
	    cargs = self._connect_args
	    self._r53 = Route53Connection(**cargs)
	return self._r53

    def get_all_r53_zones(self):
        """Return a list of all Route53 hosted zones.
           Note: latest boto has a r53.get_zones() function"""
	if not self.__dict__.has_key("_r53_zones"):
	    r53 = self.get_r53()
            raw_zones = r53.get_all_hosted_zones()['ListHostedZonesResponse']['HostedZones']
            zones = []
            for raw_zone in raw_zones:
                zones.append(R53Zone(r53, raw_zone))
            self._r53_zones = zones
        return self._r53_zones

    def find_r53_zone_for(self, fqdn):
	"""Find the DNS zone that contains fqdn. Return is ID."""
        zones = self.get_all_r53_zones()

	# Make sure the FQDN ends with "." (the zone names we compare
	# with do
	if not fqdn.endswith("."):
	    fqdn = fqdn+"."

        for zone in zones:
            if fqdn.endswith("."+zone.name):
		break
	else:
	    raise Exception("No Route53 dns zone found for %s" % fqdn)
	return zone.id

    def add_r53_record(self, fqdn, type, value, ttl=60):
	"""Add a record to Route53"""
	r53 = self.get_r53()
	zone_id = self.find_r53_zone_for(fqdn)
	changes = ResourceRecordSets(r53, zone_id)
	change = changes.add_change("CREATE", fqdn, type, ttl)
	change.add_value(value)
	changes.commit()

    def delete_r53_record(self, fqdn, type, value, ttl=60):
        """Remove a record from Route53"""
	r53 = self.get_r53()
	zone_id = self.find_r53_zone_for(fqdn)
	changes = ResourceRecordSets(r53, _r53_zone_id)
	change = changes.add_change("DELETE", fqdn, type, ttl)
	change.add_value(value)
	changes.commit()

    def change_r53_record(self, fqdn, type, value, ttl=60):
        """Change a record in Route53 - record must already exist"""
        delete_r53_record(fqdn, type, value, ttl)
        add_r53_record(fqdn, type, value, ttl)

    def add_a_record(self, fqdn, ip_addr, ttl=60):
	"""Add an A reocrd to Route53"""
        self.add_r53_record(fqdn, "A", ip_addr, ttl)

    def delete_a_record(self, fqdn, ip_addr, ttl=60):
	"""Remove an A reocrd from Route53"""
        self.delete_r53_record(fqdn, "A", ip_addr, ttl)

    def add_cname(self, fqdn, realname, ttl=60):
	"""Add a CNAME to Route53"""
        self.add_r53_record(fqdn, "CNAME", realname, ttl)

    def delete_cname(self, fqdn, realname, ttl=60):
	"""Remove a CNAME from Route53"""
        self.delete_r53_record(fqdn, "CNAME", realname, ttl)

    def get_iam(self):
        if not self.__dict__.has_key("_iam"):
	    cargs = self._connect_args
	    self._iam = IAMConnection(**cargs)
	return self._iam

    def find_cert(self, name):
        """Get ARN for certificate with specified name

        Expects that there is one and only one certificate with the name.
        Throws an exception if exactly one match is not found.

        """
        if not self.__dict__.has_key("_certs"):
            self._certs = self.get_iam().get_all_server_certs()

        matches = []
        for certinfo in self._certs["list_server_certificates_response"]["list_server_certificates_result"]["server_certificate_metadata_list"]:
            if certinfo["server_certificate_name"] == name:
                matches.append(certinfo["arn"])
        if not matches:
            raise Exception("cert not found: "+name)
        if len(matches) > 1:
            raise Exception("found %d certs with name: %s"
                    % (len(matches), name))
        return matches[0]

    def get_sdb(self):
        """Get connection to the simpledb service"""
        if not self.__dict__.has_key("_sdb"):
	    cargs = self._connect_args
	    self._sdb = boto.sdb.connect_to_region(self._region, **cargs)
	return self._sdb

    def get_domain(self, name, auto_create=False):
        """Get a domain in the simpledb service"""
        sdb = self.get_sdb()
        try:
            dom = sdb.get_domain(name)
        except boto.exception.SDBResponseError:
            if auto_create:
                dom = sdb.create_domain(name)
            else:
                raise
        return dom

