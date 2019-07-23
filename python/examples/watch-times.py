import fileinput
import re
from decimal import Decimal

current_requests = {}
try:
    for line in fileinput.input():
        if 'pyserver-fcgi-timer' not in line:
            continue
        elif 'request started' in line:
            pid, path = re.match(r'.*\[(\d+)\]:.* - (.*)', line).groups()
            current_requests[pid] = path
        elif 'request ended' in line:
            pid, duration = re.match(r'.*\[(\d+)\]:.* ([\d\.]+)ms', line).groups()
            if pid not in current_requests:
                continue
            path = current_requests.pop(pid)
            print path, duration
except KeyboardInterrupt:
    pass
