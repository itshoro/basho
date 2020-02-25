import json
import threading
import time
from random import randint, uniform

from utils.db_mediator import Mediator
import utils.server_constants as constants

import requests

class DeviceEmulator:
    def __init__(self, deviceNames = []):
        self.deviceThreads = []

        if len(deviceNames) > 0:
            for name in deviceNames:
                self.deviceThreads.append(DeviceEmulationThread(1, name)) # Emulate for base user.

    def startAndJoinAfterXSeconds(self, seconds = 10):
        for thread in self.deviceThreads:
            thread.start()

        time.sleep(seconds)
        for thread in self.deviceThreads:
            thread.running = False
            thread.join()

class DeviceEmulationThread(threading.Thread):
    def __init__(self, user, name):
        threading.Thread.__init__(self)
        self.mediator = Mediator()

        self.mediator.create()
        try:
            jsonRequest = f'''
            {{
                "type": "{constants.TYPE_ADD_DEVICE}",
                "userId": "1",
                "title": "{name}"
            }}
            '''
            token = self.mediator.send(jsonRequest)
            print(f"Device({name}) has received the token: {token}")

            self.device = Device(name, token)
            self.running = True
        except:
            print(f"Device({name}) is unable to receive a token.")
            self.running = False
        finally:
            self.mediator.close()


    def run(self):
        while (self.running):
            self.device.sendData(randint(0, 9999))
            time.sleep(uniform(0.6, 3.6))

class Device:
    def __init__(self, name, token):
        self.url = ("127.0.0.1", 8080)
        self.token = token
        self.name = name

        self.mediator = Mediator()

    def sendData(self, data):
        self.mediator.create()
        try:
            jsonRequest = f'''
            {{
                "type": "{constants.TYPE_ADD_DEVICE_DATA}",
                "device_token": "{self.token}",
                "density": "{data}"
            }}
            '''
            print(f"{self.name}({self.token}) sends {data}")
            self.mediator.send(jsonRequest)
        except:
            print(f"Device({self.name}) is unable to send {data}")
        finally:
            self.mediator.close()

de = DeviceEmulator([
    "pede",
    "mariu",
    "timmeh"
])
de.startAndJoinAfterXSeconds()