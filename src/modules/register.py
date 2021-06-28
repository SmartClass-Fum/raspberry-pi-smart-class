import logging
import socket

logger = logging.getLogger(__name__)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def register_device(api, class_name, class_id):
    logger.info("start register device")
    ip = get_ip()
    class_name = class_name
    class_id = class_id
    _, status = api.register_device(ip, class_name, class_id)
    return status
