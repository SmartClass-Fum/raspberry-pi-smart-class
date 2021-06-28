import base64
import os
import re
import time
from threading import Thread

from gpiozero import MotionSensor
from picamera import PiCamera


def _encode_to_server(file_path):
    time_stamp = int(re.search(r'\d+', file_path).group())
    image_64 = base64.encodebytes(open(file_path, "rb").read())
    return time_stamp, image_64


def _handle_camera(api, camera, pir, sampling_rate, delay):
    camera.start_preview()
    while True:  # todo handle error
        pir.wait_for_motion(sampling_rate)
        file_path = f'/tmp/image_{int(time.time())}.jpg'
        camera.capture(file_path)
        time_stamp, encode_image = _encode_to_server(file_path)
        api.camera_capture(time_stamp, encode_image)
        os.remove(file_path)
        time.sleep(delay)
    camera.stop_preview()


def start_camera(api, pir_pin, height, width, sampling_rate, delay):
    camera = PiCamera()
    pir = MotionSensor(int(pir_pin))
    camera.resolution = (int(height), int(width))
    thread = Thread(target=_handle_camera, args=(api, camera, pir, int(sampling_rate), int(delay)))
    thread.daemon = True
    thread.start()
    return thread
