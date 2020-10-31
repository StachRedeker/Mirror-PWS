import sys
import time
from datetime import datetime

while True:
    time.sleep(1)
    print("The time is: ", datetime.now().strftime("%H:%M:%S"))

    sys.stdout.flush()

