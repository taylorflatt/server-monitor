import os
import subprocess
import sys
import threading
import time
import logging

import requests

LOG = logging.getLogger('')

# Default number of seconds until the next ping attempt.
DEFAULT_TIMEOUT = 20

# The amount of time we wait until the next attempted status check.
timeout = DEFAULT_TIMEOUT

# The minimum threshold before we will actually attempt to restart the server.
retries = 3

# Represents the number of attempts since it was determined to be down. 
attempts = 0

# Contains the last time when it was restarted.
lastRestarted = 0

def main():
    """
    Maintains the main timer loop based on an exponential backoff function to determine 
    timings between status checks.
    """

    setupLogger(LOG)
    LOG.debug("")
    LOG.debug("==============================")
    LOG.debug("Started Server Monitor")
    LOG.debug("==============================")

    while True:
        t = threading.Timer(timeout, ping)
        t.run()

def ping():
    """
    If the server cannot be pinged, it is manually restarted.
    There is a cooldown period between attempts at restarting.
    """

    global timeout
    global retries
    global attempts
    global lastRestarted

    if not canRestart():
        LOG.info("Cooldown for restart attempt not elapsed.")
        return

    LOG.debug("Number of attempts = " + str(attempts) + ", previous timeout = " + str(timeout))
    timeout = evaluateNewTimeout()
    LOG.debug("New timeout = " + str(timeout))

    result = subprocess.check_output('powershell.exe tnc ${LOCAL_IP} -port ${LOCAL_PORT}', shell=True)
    if "DestinationHostUnreachable" in str(result):
        LOG.info("Server unreachable.")
        resetRetries()
    if "False" in str(result):
        LOG.info("Server not available.")
        attempts += 1

        # Only attempt to restart the server if it has failed 3 times in a row.
        if retries != 0:
            retries -= 1
            LOG.info("Retry attemps remaining = " + str(retries))
        else:
            LOG.info("Restarting server.")
            lastRestarted = getCurrentTimeInMillis()
            resetRetries()
            requests.post('{IFTTT_WEBHOOK_KEY}')
    else:            
        LOG.info("Server available.")
        resetRetries()
        attempts = 0

def canRestart():
    """
    Returns true if there has been 3 minutes since the previous restart attempt, false otherwise.
    """

    currentTime = getCurrentTimeInMillis()
    futureTime = int(round(60 * 3 * 1000))
    if lastRestarted + futureTime > currentTime:
        LOG.debug("Cannot restart.")
        LOG.debug("currentTime=" + str(currentTime))
        LOG.debug("futureTime=" + str(futureTime))
        LOG.debug("lastRestarted=" + str(lastRestarted))
        return False
    else:
        LOG.debug("Can restart.")
        return True

def evaluateNewTimeout():
    """
    Exponential backoff function to determine our timeout timer so we overly saturate the remote host.
    """

    return DEFAULT_TIMEOUT if attempts == 0 else ((2**attempts) - 1) + timeout

def resetRetries():
    """
    Resets the retry count to 3.

    Parameters:
    retries (int): The retries to reset.
    """

    global retries
    LOG.debug("Resetting retries from " + str(retries) + " to 3.")
    retries = 3

def getCurrentTimeInMillis():
    """
    Returns the current time in millis.
    """

    return int(round(time.time() * 1000))

def setupLogger(logger):
    """
    Sets the parameters for the logger.

    Parameters:
    logger: The logger to configure.
    """

    logger.setLevel(logging.DEBUG)
    channel = logging.StreamHandler()
    channel.setLevel(logging.INFO)

    fileHandler = logging.FileHandler('ping_output.log')
    fileHandler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fileHandler.setFormatter(formatter)
    channel.setFormatter(formatter)

    logger.addHandler(channel)
    logger.addHandler(fileHandler)

main()
