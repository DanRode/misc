#!/usr/bin/env python
"""Test autoscale

Usage: autoscale_test [OPTIONS]

Create an autoscale group that will send SNS notification as instance are created.
"""

import sys
import re
import inspect
from optparse import OptionParser
from webops import botoplus
from boto.ec2.autoscale import AutoScaleConnection
from boto.ec2.autoscale import LaunchConfiguration
from boto.ec2.autoscale import AutoScalingGroup
from boto.ec2.autoscale import Tag
from boto.sqs.connection import SQSConnection
from boto.sqs.message import RawMessage


class Script(object):
    def main(self, argv):
	"Run command line"

	#--------
	# Process command line (in argv)
	usage, description = __doc__.split("\n\n", 4)[1:3]
	usage = re.sub(r"^Usage:\s+", "", usage)
	parser = OptionParser(usage=usage, description=description)
        botoplus.add_options(parser)
	self._options, args = parser.parse_args(argv[1:])

        opname = "op_"+args[0]
        opcmd = None
        for name, member in inspect.getmembers(self, predicate=inspect.ismethod):
            if name == opname:
                opcmd = member
                break
        if not opcmd:
            # Unknown subcommand
            sys.stderr.write("unknown mode: %s\n" % (opname))
            parser.print_help()
            sys.exit(1)

        self._conn = AutoScaleConnection()

        # Invoke subcommand
        opcmd(args[1:])

    def op_create(self, args):
        conn = self._conn
        lc = LaunchConfiguration(name='test',
                image_id='ami-d58ff7bc', # Centos6-64 - EBS
                instance_type='t1.micro',
                spot_price=0.02,
                key_name='webops',
                security_groups=['sg-063ec469', 'sg-0657f169'],
                )
        conn.create_launch_configuration(lc)
        as_tag = Tag(key='cfhost', value = 'centos6-test-{ZONE}+',
                propagate_at_launch=True,
                resource_id='test')

        ag = AutoScalingGroup(name='test',
                availability_zones=['us-east-1a'],
                vpc_zone_identifier='subnet-b1c96fdd',
                tags=[as_tag],
                launch_config=lc,
                min_size=0,
                max_size=0,
                connection=conn,
                )
        topic = 'arn:aws:sns:us-east-1:311514151974:test'
        conn.create_auto_scaling_group(ag)

        ag.put_notification_configuration(topic, ['autoscaling:EC2_INSTANCE_LAUNCH'])

    def op_setsize(self, args):
        size = int(args[0])
        conn = self._conn
        group = conn.get_all_groups(names=['test'])[0]
        group.min_size = size
        group.max_size = size
        group.desired_capacity = size
        group.update()

    def op_list(self, args):
        conn = self._conn
        for group in conn.get_all_groups():
            print "** %s (%d-%d) **" % (group.name, group.min_size, group.max_size)
            for i in group.instances:
                print i.instance_id
            for activity in group.get_activities():
                print str(activity)

    def op_delete(self, args):
        conn = self._conn
        groups = conn.get_all_groups(names=['test'])
        if groups:
            group = groups[0]
            group.shutdown_instances()
            group.delete()

        lcs = conn.get_all_launch_configurations(names=['test'])
        if lcs:
            lc = lcs[0]
            lc.delete()

    def op_consume(self, args):
        sqs = SQSConnection()
        q = sqs.get_queue('test')
        q.set_message_class(RawMessage)
        for message in q.get_messages():
            print message.get_body()
            q.delete_message(message)




if __name__ == '__main__':
    retcode = 0
    try:
	Script().main(sys.argv)
    except KeyboardInterrupt:
	# Could put script cleanup here
	retcode = 1
    sys.exit(retcode)
