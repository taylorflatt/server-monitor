import os
import sys
import threading
import time

import requests


def main():
    while True:
        t = threading.Timer(10.0, ping)
        t.run()

def ping():
    """
    If the server cannot be pinged, it is manually restarted.
    There is a cooldown period between attempts at restarting.
    """

    if not canRestart():
        print("Cooldown for attempting to restart not over yet!")
        return

    global lastRestarted
    if os.system('ping %s -n 1' % ("{LOCAL_IP}",)):
        print("Service not available!")
        lastRestarted = getCurrentTimeInMillis()
        requests.post('https://maker.ifttt.com/trigger/plex_offline/with/key/{IFTTT_WEBHOOK_KEY}')
    else:
        print("Server available!")

def canRestart():
    """
    Returns true if there has been sufficient enough time since restarts, false otherwise.
    """

    print("lastRestarted = " + str(lastRestarted))
    currentTime = getCurrentTimeInMillis()
    print("currentTime = " + str(currentTime))
    futureTime = int(round(60 * 5 * 1000))
    print("futureTime = " + str(futureTime))
    if lastRestarted + futureTime > currentTime:
        print("CANNOT Restart!")
        return False
    else:
        print("CAN Restart!")
        return True

def getCurrentTimeInMillis():
    """
    Returns the current time in millis.
    """

    return int(round(time.time() * 1000))

# Contains the last time when it was restarted.
lastRestarted = getCurrentTimeInMillis()

main()
