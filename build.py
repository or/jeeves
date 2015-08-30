#!/usr/bin/env python
import sys
import time
from datetime import datetime

print("starting with args: {}".format(sys.argv[1:]))

print("{} did some things...".format(datetime.now()))
time.sleep(2)
print("{} did some more things...".format(datetime.now()))
time.sleep(3)

for i in range(150):
    print("line {}".format(i))
    time.sleep(0.1)

print("all done!")
