import argparse
import configparser
import logging
import os

from src.modules.camera import start_camera
from src.modules.ping import ping_test
from src.modules.read_rfid import RFIDReader, send_to_server
from src.modules.register import register_device
from src.modules.server_communication import BaseApi


def _read_config(config_path="config.ini"):
    config = configparser.ConfigParser()
    config.read(config_path)
    # List all contents
    logging.info("List all contents")
    for section in config.sections():
        logging.info("Section: %s" % section)
        for options in config.options(section):
            logging.info(
                "x %s:::%s:::%s"
                % (options, config.get(section, options), str(type(options)))
            )
    return config


def _config_logger(log_path, log_name):
    root_logger = logging.getLogger()

    file_handler = logging.FileHandler("{0}/{1}.log".format(log_path, log_name))
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    root_logger.addHandler(console_handler)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='arvan client')
    parser.add_argument('cmd', type=str,
                        help='command')
    args = parser.parse_args()

    config = _read_config()
    logging.basicConfig(
        level=getattr(logging, config['logger']['log_level'], 'INFO'),
        format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
    )
    _config_logger(config['logger']['logPath'], config['logger']['fileName'])
    api = BaseApi(config['server']['server_ip'])
    is_register = register_device(api, config['class']['class_name'], config['class']['class_id'])
    if not is_register:
        logging.error("can't register device and shutdown")
        os.exit(2)
    if args.cmd == "up":
        start_camera(api, config['motion']['pin'], config['camera']['height']
                     , config['camera']['width'], config['camera']['sampling_rate']
                     , config['camera']['delay'])
        rfid = RFIDReader(send_to_server(api))
    elif args.cmd == "down":
        pass
    elif args.cmd == "ping":
        ping_test()
    else:
        logging.warning("WTF?")
