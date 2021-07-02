import configparser
import logging
import time
import json

from mfrc522 import SimpleMFRC522

import paho.mqtt.client as mqtt

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

    file_handler = logging.FileHandler("{0}/camera-{1}.log".format(log_path, log_name))
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    root_logger.addHandler(console_handler)


def rfid_read(message, class_id, client):
    data = {'class_id': class_id,
            'rfid_message': message,
        }
    logging.error("rfid_action requested" + str(data))
    response = client.publish("fumSmartClassIot/rfid", json.dumps(data))


def _handle_rfid(reader, class_id, client):
    logging.error("Started Reading")
    try:
        while True:
            idd, message = reader.read_no_block()
            logging.error(f"A new Message has been read By RFID module. The Message: {message}")
            if message is not None or idd is not None:
                rfid_read(message, class_id, client)
            time.sleep(1)
    finally:
        logging.error("Finished Reading RFID")

def start_rfid():
    config = _read_config() 
    logging.basicConfig(
        level=getattr(logging, config['logger']['log_level'], 'DEBUG'),
        format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
    )
    _config_logger(config['logger']['logPath'], config['logger']['fileName'])
    broker_address = "broker.mqtt-dashboard.com"
    client = mqtt.Client("SmartClassFUMCameraModule")
    client.connect(broker_address)
    reader = SimpleMFRC522()
    _handle_rfid(reader, config['class']['class_id'], client)


# class RFIDReader:

#     def __init__(self, callback=None, event=None):
#         self.reader = SimpleMFRC522()
#         self.read_thread = threading.Thread(target=self.thread_main, daemon=True)
#         if callback is not None:
#             self.callback = callback
#         else:
#             self.callback = RFIDReader.default_callback
#         self.go_on = True
#         if event is None:
#             event = threading.Event()
#         self.stopped = event
#         logging.error("Trying to start the Reader thread")
#         self.read_thread.start()
#         logging.error("The RFID reader thread has started")

#     @staticmethod
#     def default_callback(message):
#         logger.info(f"Message is: {message}")

#     def thread_main(self, ):
#         logging.error("Started Reading")
#         try:
#             while self.go_on and not self.stopped.wait(1):
#                 idd, message = self.reader.read_no_block()
#                 logging.error(f"A new Message has been read By RFID module. The Message: {message}")
#                 if message is not None or idd is not None:
#                     self.callback(message)
#         finally:
#             self.go_on = False
#             logging.error("Finished Reading RFID")

#     def is_running(self):
#         return self.go_on

#     def kill_reader(self):
#         self.go_on = False
#         logger.info("The Reader is Killed")
#         return self.go_on


# def send_to_server(api):
#     api_service = api

#     def callback(message):
#         api_service.rfid_action(message)

#     return callback
