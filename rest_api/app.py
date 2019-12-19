import json

from flask import Flask, request
from flask_restful import Api, Resource, reqparse

from utils.db_mediator import Mediator
import utils.server_constants as server_constants

# TODO Consider using Flask, without REST.
# We could do something along the lines of:
# 
# + user
# | |- - /login/email/hashPassword      -> user.Id, user.sessionToken       (tries to login)
# | |- - /register/email/hashPassword   -> user.Id                          (tries to register)
# | |- - /verify/id/token               -> user.Id                          (verifies session token)
# | |- - /salt/email                    -> user.salt                        (returns the salt corresponding to the user)
# + device
# | |- - /add                           -> device.token                     (adds new device)
# | |- - /add/token/data                -> 200 / 403                        (adds data for a device, specified by the token)
# | |- - /verify/token                  -> 200 / 404                        (verifies that a device with that token exists)
# | |- - /remove/token                  -> 200 / 400                        (removes a device that has the token)
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
            "type": server_constants.TYPE_VERIFY_DEVICE,
            "token": token
        }
        try:
            self.mediator.create() # TODO DNS
            self.mediator.send(json.dumps(data))
            return "Device exists.", 200
        except (Exception):
            return "Device does not exist.", 404

    def post(self, token, data=None):
        data = {
            "type": server_constants.TYPE_ADD_DEVICE_DATA,
            "token": token,
            "data": data
        }
        try:
            self.mediator.create() # TODO DNS
            self.mediator.send(json.dumps(data))
            self.mediator.close()
            return "Data was successfully added.", 200
        except (Exception):
            return "Forbidden", 403

    def put(self):
        data = {
            "type": server_constants.TYPE_ADD_DEVICE
        }
        try:
            self.mediator.create()
            response = self.mediator.send(json.dumps(data))
            self.mediator.close()
            return response, 200
        except:
            return "Device registration failed.", 400

    def delete(self, token):
        data = {
            "type": server_constants.TYPE_DELETE_DEVICE,
            "token": token
        }
        try:
            self.mediator.create()
            self.mediator.send(json.dumps(data))
            self.mediator.close()
            return "Device deleted.", 200
        except:
            return "A device with that token doesn't exist.", 400

app = Flask(__name__)
api = Api(app)

api.add_resource(Device, "/device/<str:token>/<data>")
app.run(debug=True)