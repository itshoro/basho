from flask import Flask, request
from flask_restful import Api, Resource, reqparse

from db_mediator import Mediator
import json

# TODO Consider using Flask, without REST.
# We could do something along the lines of:
# 
# + user
# | |- - /login/email/hashPassword      -> user.Id, user.sessionToken,
# | |- - /register/email/hashPassword   -> user.Id
# | |- - /verify/id/token               -> user.Id
# | |- - /salt/email                    -> user.salt
# + device
# | |- - /add                           -> device.token         (adds new device)
# | |- - /add/token/data                -> 200 / 403            (adds data for a device, specified by the token)
# | |- - /verify/token                  -> 200 / 404            (verifies that a device with that token exists)
# | |- - /remove/token                  -> 200 / 400            (removes a device that has the token)
#
# Maybe I can also send the session token of the device owner for the device to make it "more secure". But
# this would probably be overkill.

class Device(Resource):
    def __init__(self):
        self.mediator = Mediator()
        super.__init__()

    def get(self, token):
        '''
        Returns the device id of the corresponding device token.
        '''
        data = {
            "type": "DEVICE_VERIFY",
            "token": token
        }
        try:
            self.mediator.create() # TODO DNS
            self.mediator.send(bytes(json.dumps(data), "utf-8"))
            self.mediator.close()
            return "Device exists.", 200
        except (Exception):
            return "Device does not exist.", 404

    def post(self, token, data=None):
        data = {
            "type": "DEVICE_DATA_ADD",
            "token": token,
            "data": data
        }
        try:
            self.mediator.create() # TODO DNS
            self.mediator.send(bytes(json.dumps(data), "utf-8"))
            self.mediator.close()
            return "Data was successfully added.", 200 
        except (Exception):
            return "Forbidden", 403

    def put(self):
        data = {
            "type": "DEVICE_ADD"
        }
        try:
            self.mediator.create()
            response = self.mediator.send(bytes(json.dumps(data), "utf-8"))
            self.mediator.close()
            return response, 200
        except:
            return "Device registration failed.", 400

    def delete(self, token):
        data = {
            "type": "DEVICE_DELETE",
            "token": token
        }
        try:
            self.mediator.create()
            self.mediator.send(bytes(json.dumps(data), "utf-8"))
            self.mediator.close()
            return "Device deleted.", 200
        except:
            return "A device with that token doesn't exist.", 400

app = Flask(__name__)
api = Api(app)

api.add_resource(Device, "/device/<str:token>/<data>")