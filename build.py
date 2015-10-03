#!/usr/bin/env python
import sys
import time
from datetime import datetime

print("starting with args: {}".format(sys.argv[1:]))

print("{} did some things...".format(datetime.now()))
time.sleep(2)
print("{} did some more things...".format(datetime.now()))
time.sleep(3)

sys.stderr.write("some error!\n")
sys.stderr.flush()

for i in range(15):
    print("line {}".format(i))
    sys.stdout.flush()
    time.sleep(0.1)

sys.stderr.write("another error!\n")
sys.stderr.flush()

print("all done!")
