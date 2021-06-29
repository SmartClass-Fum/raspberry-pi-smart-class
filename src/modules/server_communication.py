import json
import logging

import requests

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class BaseApi:
    register_endpoint = '/device_register'
    camera_endpoint = '/camera'
    rfid_endpoint = '/rfid'

    def header(self):
        return {
            'Accept-Language': 'en',
            'Content-Type': 'application/json',
            'authentication': self.auth_key
        }

    @staticmethod
    def check_response_status(response):
        if 200 <= response.status_code < 500:
            return True
        else:
            return False

    def __init__(self, auth_key='1234', base_url='http://localhost:8080') -> None:
        super().__init__()
        self.base_url = base_url
        self.auth_key = auth_key

        broker_address = "broker.mqtt-dashboard.com"
        self.client = mqtt.Client("SmartClassFUM")
        self.client.connect(broker_address)

    def register_device(self, ip, class_name, class_id):
        headers = self.header()
        data = {'ip': ip,
                'class_name': class_name,
                'class_id': class_id
                }
        logger.debug("register_device requested" + str(data))
        response = requests.post(f'{self.base_url}{BaseApi.register_endpoint}',
                                 headers=headers, data=json.dumps(data, ensure_ascii=False).encode('utf-8'))
        logger.debug("register_device response" + str(response))

        return response.text, BaseApi.check_response_status(response)

    def camera_capture(self, time_stamp, encode_image):
        headers = self.header()
        data = {'time_stamp': time_stamp,
                'encode_image': encode_image
                }
        logger.debug("camera_capture requested" + str(data))
        # response = requests.post(f'{self.base_url}{BaseApi.camera_endpoint}',
        #                          headers=headers, data=json.dumps(data, ensure_ascii=False).encode('utf-8'))
        response = self.client.publish("fum_smart_class_iot/camera", data)
        logger.debug("camera_capture response" + str(response))

        return response.text, BaseApi.check_response_status(response)

    def rfid_action(self, rfid_message):
        headers = self.header()
        data = {'rfid_message': rfid_message,
                }
        logger.debug("rfid_action requested" + str(data))
        response = requests.post(f'{self.base_url}{BaseApi.rfid_endpoint}',
                                 headers=headers, data=json.dumps(data, ensure_ascii=False).encode('utf-8'))
        logger.debug("rfid_action response" + str(response))

        return response.text, BaseApi.check_response_status(response)
