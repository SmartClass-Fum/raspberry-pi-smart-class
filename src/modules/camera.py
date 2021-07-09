import configparser
import base64
import os
import re
import time
import json
# from threading import Thread

import logging

from gpiozero import MotionSensor
from picamera import PiCamera

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
    return root_logger


def _encode_to_server(file_path):
    time_stamp = int(re.search(r'\d+', file_path).group())
    with open(file_path, 'rb') as f:
        image_64 = base64.b64encode(f.read()).decode('utf-8')
    return time_stamp, image_64


def _handle_camera(class_id, camera, sampling_rate, delay, client, logger):
    camera.start_preview()
    file_path = None
    while True:  # todo handle error
        try:
            # pir.wait_for_motion(sampling_rate)
            if file_path is not None:
                os.remove(file_path)
            file_path = f'/tmp/image_{int(time.time())}.jpg'
            print(file_path)
            print(camera.capture(file_path,))
            time_stamp, encode_image = _encode_to_server(file_path)
            camera_capture(class_id, time_stamp, encode_image, client, logger)
            
            time.sleep(delay)
        except Exception as e:
            logger.error(e.traceback())
    camera.stop_preview()

def camera_capture(class_id, time_stamp, encode_image, client, logger):
        # headers = self.header()
        data = {'class_id': class_id,
                'time_stamp': time_stamp,
                'encode_image': encode_image
                }
        # print(data)
        logger.info("camera_capture requested ")
        # response = requests.post(f'{self.base_url}{BaseApi.camera_endpoint}',
        #                          headers=headers, data=json.dumps(data, ensure_ascii=False).encode('utf-8'))
        response = client.publish("fumSmartClassIot/camera", json.dumps(data))
        # response = client.publish("fumSmartClassIot/camera", "HELOOOO")
        logger.info("camera_capture response" + str(response))
        

def start_camera(pir_pin, height, width, sampling_rate, delay):
    config = _read_config() 
    logging.basicConfig(
        level=getattr(logging, config['logger']['log_level'], 'DEBUG'),
        format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
    )
    logger = _config_logger(config['logger']['logPath'], config['logger']['fileName'])
    broker_address = "broker.mqtt-dashboard.com"
    # broker_address = "mqtt.eclipse.org"
    client = mqtt.Client("SmartClassFUMCameraModule123")
    client.connect(broker_address)
    camera = PiCamera()
    logging.error("Starting Camera")
    # pir = MotionSensor(int(pir_pin))
    camera.resolution = (int(height), int(width))
    _handle_camera(config['class']['class_id'], camera, int(sampling_rate), int(delay), client, logger)
    # thread = Thread(target=_handle_camera, args=(api, camera, pir, int(sampling_rate), int(delay)))
    # thread.daemon = True
    # thread.start()
    # logging.error("Started Thread of Camera")
    # return thread
