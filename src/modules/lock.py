import configparser
import logging
import time
import json
import RPi.GPIO as GPIO

import paho.mqtt.client as mqtt

config = None
logger = None

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

    file_handler = logging.FileHandler("{0}/lock-{1}.log".format(log_path, log_name))
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    root_logger.addHandler(console_handler)
    
    return root_logger

def on_message(client, userdata, message):
    global config
    global logger

    # logger.info("Started lock handler.")
    idd, state = message.payload.decode('utf-8').split("&&")
    logger.error(f"{idd} : {state}")
    if idd == config['class']['class_id']:
        if state == '1':
            GPIO.output(int(config['lock']['relay']), 1)
            logger.info("Relay is 1")
            logger.error("Relay is 1")
        elif state == '0':
            GPIO.output(int(config['lock']['relay']), 0)
            logger.info("Relay is 0")
            logger.error("Relay is 0")
        else :
            logger.info(f"SOMETHING ELSE IS RECIEVED: {state}")
            pass

# def on_log(client, obj, level, string)



def start_lock():
    global config
    global logger
    config = _read_config()
    logging.basicConfig(
        level=getattr(logging, config['logger']['log_level'], 'DEBUG'),
        format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
    )
    logger = _config_logger(config['logger']['logPath'], config['logger']['fileName'])
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(int(config['lock']['relay']), GPIO.OUT)
    GPIO.output(int(config['lock']['relay']), 0)

    broker_address = "broker.mqtt-dashboard.com"
    client = mqtt.Client("SmartClassFUMLockModule")
    client.on_message = on_message
    client.connect(broker_address)
    client.subscribe("fumSmartClassIot/lock")

    rc = 0
    while rc == 0:
        rc = client.loop()
    # GPIO.cleanup()
    if rc != 0:
        logger.error("Client loop exited. rc value is `{rc}`.")







