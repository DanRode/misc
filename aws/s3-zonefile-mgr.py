#!/usr/bin/env python
"""
Manage a set of DNS zone files stored in S3
"""
# This script features examples of a few common s3 tasks.
# While the files are ostensibly dns zone files, the content is
# meaningless and could contain any text. The files are stored in a
# folder for a look at working with folder/file names

import os
import sys
import re
from time import sleep
from optparse import OptionParser
import boto

def upload_zonefile(conn, bucket_name, zonefile, filename):
    """Creates or replaces a zone file"""
    print "Uploading %s to %s/%s" % (filename, bucket_name, zonefile)
    bucket = conn.get_bucket(bucket_name)
    key = bucket.new_key(zonefile)
    key.set_contents_from_filename(filename,)
    
def delete_zonefile(conn, bucket_name, zonefile):
    """Deletes a zone file"""
    path, file = zonefile.split('/', 1)
    bucket = conn.get_bucket(bucket_name)
    key = bucket.get_key(zonefile)
    print "This will delete %s Are you sure [y/n]:" % file,
    check = raw_input()
    if check == "y":
        bucket.delete_key(key)

def get_zonefile(conn, bucket_name, zonefile):
    """ Prints out the records of a given zone"""
    path, file = zonefile.split('/', 1)
    print "Records for %s" % file
    bucket = conn.get_bucket(bucket_name)
    key = bucket.get_key(zonefile)
    print key.get_contents_as_string()

def list_zonefiles(conn, bucket_name):
    """Lists all files in the dns-zones folder that match pub.*[com|net]"""
    print "List of zone files"
    bucket = conn.get_bucket(bucket_name)
    keys =  bucket.list("dns-zones")
    for key in keys:
        path, zonefile = key.name.split('/', 1)
        if re.match('^pub-.*[com|net]$', zonefile):
            print zonefile

def list_metadata(conn, bucket_name):
    print "Metadata for zone files"
    bucket = conn.get_bucket(bucket_name)
    keys =  bucket.list("dns-zones")
    files = 0
    size = 0
    for key in keys:
        path, zonefile = key.name.split('/', 1)
        if re.match('^pub-.*[com|net]$', zonefile):
            files = files + 1
            size = size + key.size
            print "%s" % key.name
            print "  Size: %s" % key.size
            print "  Modified: %s" % key.last_modified
            print "  Storage Class: %s" % key._storage_class
            print ""
    print "TOTAL: %s files, %s bytes" % (files, size)

def main():
    parser = OptionParser(usage="Usage: %prog [options] zone")
    parser.add_option('-l', '--list-zones',
            action = 'store_true',
            default = False,
            dest = 'list',
            help = 'Lists all zone files', )
    parser.add_option('-m', '--metadata',
            action = 'store_true',
            default = False,
            dest = 'metadata',
            help = 'Prints files metadata', )
    parser.add_option('-d', '--delete-zone',
            action = 'store_true',
            default = False,
            dest = 'delete',
            help = 'Deletes the specified zone', )
    parser.add_option('-p', '--print-zone',
            action = 'store_true',
            default = True,
            dest = 'getzone',
            help = 'Print the contents of the specified zone', )
    parser.add_option('-u', '--upload', 
            action='store', 
            dest='filename', 
            help="Uploads zone file to s3", )
                        
    options, args = parser.parse_args()

    bucket_name = 'rode-configs'
    AWS_ACCESS_KEY_ID = ''
    AWS_SECRET_ACCESS_KEY = ''
    conn = boto.connect_s3()

    if options.list:
        list_zonefiles(conn, bucket_name)
    elif options.metadata:
        list_metadata(conn, bucket_name)
    elif len(args) != 1:
        parser.error("Wrong number of arguments")
    else:
        zone =args[0].strip()
        zone = zone.rstrip('\.')
        # If we get the filename instead if the zone, fix it
        tmp = re.search(r'^pub-(.*)$', zone)
        if tmp:
            zone = tmp.group(1)
        if zone.endswith("com") or zone.endswith("net"):
            zonefile = "dns-zones/pub-%s" % zone
        else:
            parser.error("'%s' is not a valid zone name" % zone)
        if options.filename:
            upload_zonefile(conn, bucket_name, zonefile, options.filename)
            # Sleep for 2 seconds to give s3 time to process the file
            sleep(2)
            get_zonefile(conn, bucket_name, zonefile)
        elif options.delete:
            delete_zonefile(conn, bucket_name, zonefile)
            list_zonefiles(conn, bucket_name)
        else:
            get_zonefile(conn, bucket_name, zonefile)

if __name__ == '__main__':
    main()
