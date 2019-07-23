#!/usr/bin/env python
import argparse
import sys
 
parser = argparse.ArgumentParser(description='script to copy one file to another')
 
parser.add_argument('-v', '--verbose',
    action="store_true",
    help="verbose output" )
 
parser.add_argument('-R',
    action="store_false",
    help="Copy all files and directories recursively")
 
parser.add_argument('infile',
    type=argparse.FileType('r'), 
    help="file to be copied")
 
parser.add_argument('outfile',
    type=argparse.FileType('w'),
    help="file to be created")
 
args = parser.parse_args()
