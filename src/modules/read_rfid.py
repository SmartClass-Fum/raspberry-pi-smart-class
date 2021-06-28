import threading
import logging

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522


logger = logging.getLogger()

class RFIDReader:

    def __init__(self, cback=None,):
        self.reader = SimpleMFRC522()
        self.read_thread = threading.Thread(target=self.thread_main, daemon=True, )
        if cback != None:
            self.cback = cback
        else:
            self.cbakc = self.default_cback
        self.go_on = True
        logging.info("Trying to start the Reader thread")
        self.read_thread.start()
        logging.info("The RFID reader thread has started")


    def default_cback(self, msg):
        print(f"Message is: {msg}")


    def thread_main(self,):
        logging.info("Started Reading")
        try:
            while self.go_on:
                idd, msg = self.reader.read()
                logging.info(f"A new Message has been read By RFID module. The Message: {msg}")
                if msg != None:
                    self.cback(msg)
        finally:
            self.go_on = False
            logging.info("Finished Reading RFID")

    def is_running(self,):
        return self.go_on

    def kill_reader(self,):
        self.go_on = False
        logger.info("The Reader is Killed")
        return self.go_on





