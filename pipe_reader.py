#!/usr/bin/python

import sys

while 1:
    with open('/home/pi/cec', 'r', 0) as p:
        print(p.read())
        sys.stdout.flush()
