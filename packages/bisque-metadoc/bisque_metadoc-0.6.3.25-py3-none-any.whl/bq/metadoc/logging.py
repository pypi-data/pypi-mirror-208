#  Utilities to add context parameters to logging
#

# pylint: disable=unused-import
import logging
import socket
from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    NOTSET,
    WARNING,
    critical,
    error,
    exception,
    info,
    log,
    warning,
)

old_getLogger = logging.getLogger


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


class BQContextFilter(logging.Filter):
    """ """

    def __init__(self):
        self.ip_addr = get_ip()

    def filter(self, record):
        record.log_ip = self.ip_addr
        return True


BQFilters = [BQContextFilter()]


def getLogger(*args, **kw):
    lgg = old_getLogger(*args, **kw)
    for log_filter in BQFilters:
        lgg.addFilter(log_filter)
    return lgg


logging.getLogger = getLogger
