#!/usr/bin/env python
import os
import re
import sys
import time
import datetime

timecheck = int(os.getenv('TIMECHECK',3600))

for line in sys.stdin:
      line=line.rstrip()
      parsed_line = map(''.join, re.findall(r'\"(.*?)\"|\[(.*?)\]|(\S+)', line))
      if parsed_line[5][0] == '5':
        delta = datetime.datetime.now() - datetime.timedelta(seconds=timecheck)
        tt = datetime.datetime.strptime(parsed_line[3][:-6], "%d/%b/%Y:%H:%M:%S")
        if tt >= delta: print line
