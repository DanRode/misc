#! /usr/bin/env python


file = open('/home/drode/sqs.msg2.txt', 'r')
json_string = file.read()

import json
data = json.loads(json_string)

#if data["EC2InstanceId"]:
#    print data["EC2InstanceId"]

for key in data:
    if key == "Message":
        print data[key]
        message = json.loads(data[key])
        for mkey in message:
            print "MKEY: %s \n%s" % (mkey, message[mkey])




#print json.dumps(data)
