import sys
import time
from datetime import datetime


def dataOut(key, data):
    print(key, "_", data)
    sys.stdout.flush()


while True:
    time.sleep(0.1)
    dataOut("time", datetime.now().strftime("%H:%M:%S"))
