import requests
import json

import threading
import time
from random import randint, uniform

class DeviceEmulator:
    def __init__(self, deviceTokens = [], amount = 4):
        if amount < 0: raise ValueError("Must be positive integer")
        self.deviceThreads = []
        

        if len(deviceTokens) > 0:
            for deviceToken in deviceTokens:
                self.deviceThreads.append(DeviceEmulationThread(deviceToken))

        for i in range(amount):
            self.deviceThreads.append(DeviceEmulationThread())

    def startAndJoinAfterXSeconds(self, seconds = 10):
        for thread in self.deviceThreads:
            thread.start()
            thread.join()

            time.sleep(seconds)
            thread.running = False

class DeviceEmulationThread(threading.Thread):
    def __init__(self, token = None):
        threading.Thread.__init__(self)
        if token == None:
            # TODO: Get new token from REST.
            raise NotImplementedError()
        self.device = Device(token)
        self.running = True

    def run(self):
        while (self.running):
            self.device.sendData(randint(0, 9999))
            time.sleep(uniform(0.6, 3.6))

class Device:
    def __init__(self, token = None):
        self.url = ("127.0.0.1", 8080)
        self.token = token

    # TODO use mediatior to GET REST.
    def verify(self):
        data = {
            "token": self.token
        }
        r = requests.get(self.url, data=data)
        return r.status_code == 200

    # TODO use mediatior to post to REST.
    def sendData(self, data):
        requests.post(self.url, data=data)