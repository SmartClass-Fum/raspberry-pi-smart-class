import json
import logging

import requests

logger = logging.getLogger(__name__)


class BaseApi:
    register_url = '/device_register'

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

    def register_device(self, ip, class_name, class_id):
        headers = self.header()
        data = {'ip': ip,
                'class_name': class_name,
                'class_id': class_id
                }
        logger.debug("register_device requested" + str(data))
        response = requests.post(f'{self.base_url}{BaseApi.register_url}',
                                 headers=headers, data=json.dumps(data, ensure_ascii=False).encode('utf-8'))
        logger.debug("register_device response" + str(response))

        return response.text, BaseApi.check_response_status(response)
