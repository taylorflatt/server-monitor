import os
import sys
import threading
import time


def main():
    while True:
        t = threading.Timer(10.0, ping)
        t.run()

def ping():
    """
    If the server cannot be pinged, it is manually restarted.
    There is a cooldown period between attempts at restarting.
    """

    global lastRestarted
    if not os.system('ping %s -n 1' % ("192.168.0.180",)) and canRestart():
        print("Service not available!")
        lastRestarted = getCurrentTimeInMillis()
    else:
        print("Server available!")

def canRestart():
    """
    Returns true if there has been sufficient enough time since restarts, false otherwise.
    """

    print("lastRestarted = " + str(lastRestarted))
    currentTime = getCurrentTimeInMillis()
    print("currentTime = " + str(currentTime))
    futureTime = int(round(5 * 1000))
    print("futureTime = " + str(futureTime))
    if lastRestarted + futureTime > currentTime:
        print("CAN Restart!")
        return True
    else:
        print("CANNOT Restart!")
        return False

def getCurrentTimeInMillis():
    """
    Returns the current time in millis.
    """

    return int(round(time.time() * 1000))

# Contains the last time when it was restarted.
lastRestarted = getCurrentTimeInMillis()

main()
