import logging
import os

logger = logging.getLogger(__name__)


def ping_test():
    hostname = "8.8.8.8"
    response = os.system("ping -c 1 " + hostname)
    # and then check the response...
    if response == 0:
        ping_status = "Network Active"
    else:
        ping_status = "Network Error"
    logger.info(ping_status)
    return response
