import logging
import threading

from mfrc522 import SimpleMFRC522

logger = logging.getLogger(__name__)


class RFIDReader:

    def __init__(self, callback=None):
        self.reader = SimpleMFRC522()
        self.read_thread = threading.Thread(target=self.thread_main, daemon=True)
        if callback is not None:
            self.callback = callback
        else:
            self.callback = RFIDReader.default_callback
        self.go_on = True
        logging.info("Trying to start the Reader thread")
        self.read_thread.start()
        logging.info("The RFID reader thread has started")

    @staticmethod
    def default_callback(message):
        logger.info(f"Message is: {message}")

    def thread_main(self, ):
        logging.info("Started Reading")
        try:
            while self.go_on:
                idd, message = self.reader.read()
                logging.info(f"A new Message has been read By RFID module. The Message: {message}")
                if message is not None:
                    self.callback(message)
        finally:
            self.go_on = False
            logging.info("Finished Reading RFID")

    def is_running(self):
        return self.go_on

    def kill_reader(self):
        self.go_on = False
        logger.info("The Reader is Killed")
        return self.go_on


def send_to_server(api):
    api_service = api

    def callback(message):
        api_service.rfid_action(message)

    return callback
