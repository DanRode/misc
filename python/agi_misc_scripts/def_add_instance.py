def add_instance(hostname, options):
    """Create a running ec2 instance"""
    zone = 'us-east-1b'
    conn = botoplus.AWSConnection(options, region=zone[:-1])
    ec2 = conn.get_ec2()
    ami_id = 'ami-3de27654'

    reservation = ec2.run_instances(ami_id,
                        key_name='webops',
                        security_group_ids=['sg-89fd08e6',],
                        instance_type='m1.small',
                        placement='us-east-1b',
                        subnet_id='subnet-a9d573c5',
                        )

    debug("Reservation: %s" % reservation)

    # Get the Instance object inside the Reservation object
    # returned by EC2.
    instance = reservation.instances[0]

    print "Created Instance: %s" % instance
    print "Starting Instance..."
    # Wait for instance to be running before tagging (sometimes fails before)
    while True:
        debug('Instance state: %s' % instance.state)
        if (instance.state == 'running'):
            break
        elif (instance.state == 'terminated'):
            raise UserError("Instance reservation failed. Please try again.")
        else:
            time.sleep(5)
            instance.update()



