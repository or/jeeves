#!/usr/bin/env python
import random
import sys
import time
from datetime import datetime

print("starting with args: {}".format(sys.argv[1:]))

print("{} did some things...".format(datetime.now()))
time.sleep(2)
print("{} did some more things...".format(datetime.now()))
time.sleep(3)

for i in range(random.randint(100, 400)):
    print("line {}".format(i))
    sys.stdout.flush()
    time.sleep(0.1)

print("all done!")
