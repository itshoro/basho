import json
import hashlib
import secrets
import sys
import os

import cherrypy

from template import TemplateHandler
from utils.db_mediator import Mediator
import utils.server_constants as server_constants

# Because we send the error messages as plain text instead of a full blown error page.
class CustomHTTPError(cherrypy.HTTPError):
    def __init__(self, status, message):
        super().__init__(status, message)

    def set_response(self):
        super().set_response()
        response = cherrypy.serving.response
        response.headers["Content-Length"] = len(self._message.encode("utf-8"))
        response.body = self._message.encode("utf-8")

    def __str__(self):
        return self._message

# TODO: Test what happens when something like the following happens:
# - user tries to login
# - correct credentials
# - GET_SALT => user salt
# - database handler now closes suddenly
# - LOGIN => Timeout on DB => ?

class LoginHandler:
    def __init__(self):
        self.view = TemplateHandler(os.path.join(sys.path[0], "templates"))
        self.formState = 0 # 0 = Login, 1 = Register
        self.forms = ["login", "register"]

    @cherrypy.expose
    def getDevices(self, owner):
        jsonRequest = f'''
            {{
                "type": "{server_constants.TYPE_GET_DEVICES}",
                "owner": "{owner}"
            }}
        '''
        mediator = Mediator()
        mediator.create()
        try:
            data = mediator.send(jsonRequest)
            return data
        except:
            raise CustomHTTPError(400, server_constants.ERROR_DB_UNREACHABLE)
        finally:
            mediator.close()

    @cherrypy.expose
    def receiveData(self, device):
        jsonRequest = f'''
            {{
                "type": "{server_constants.TYPE_GET_DATA}",
                "id": "{device}"
            }}
        '''
        mediator = Mediator()
        mediator.create()
        try:
            data = mediator.send(jsonRequest)
            return data
        except:
            raise CustomHTTPError(400, server_constants.ERROR_DB_UNREACHABLE)
        finally:
            mediator.close()

    @cherrypy.expose
    def index(self, error = None):
        if (len(cherrypy.request.cookie) == 2 and cherrypy.request.cookie["token"]):
            try:
                return self.tryValidateAndRecoverSession()
            except:
                return self.view.create_view("login", { "form": "login", "error": server_constants.ERROR_SERVER_UNREACHABLE })
        else:
            context = {
                "form": "login",
                "error": str(error) if error else None
            }
            return self.view.create_view("login", context)

    @cherrypy.expose
    def register(self, email, password):
        salt = secrets.token_hex(8) # 16 character random string, ref: https://stackoverflow.com/a/50842164
        
        hashedPassword = self.createSaltedPassword(password, salt)
        jsonRequest = f'''
            {{
                "type": "{server_constants.TYPE_REGISTER_USER}",
                "email": "{email}",
                "password": "{hashedPassword}",
                "salt": "{salt}"
            }}
        '''
        mediator = Mediator()
        mediator.create()
        try:
            id = mediator.send(jsonRequest)
        except:
            raise CustomHTTPError(400, server_constants.ERROR_USER_ALREADY_EXISTS)
        finally:
            mediator.close()

    def redirectToHome(self):
        return self.view.create_view("index", None, None)

    def createSaltedPassword(self, password, salt):
        passHash = hashlib.sha1()
        passHash.update(password.encode("utf-8"))
        passHash.update(salt.encode("utf-8"))

        return passHash.hexdigest()

    def clearCookies(self):
        for c in cherrypy.response.cookie:
            cherrypy.response.cookie[c]["expires"] = 0

    def tryValidateAndRecoverSession(self):
        # Validate session token on the server and check wether it's expired.
        
        # If it is expired, the db will close the connection, we will redirect
        # the user to the login page with an error message.

        if not cherrypy.request.cookie["user_id"]:
            self.clearCookies()
            return self.index(CustomHTTPError(403, server_constants.ERROR_SESSION_EXPIRED))

        jsonRequest = f'''
            {{
                "type": "{server_constants.TYPE_VALIDATE_SESSION}",
                "token": "{cherrypy.request.cookie["token"].value}",
                "user_id": "{cherrypy.request.cookie["user_id"].value}"
            }}
        '''
        mediator = Mediator()
        mediator.create()
        try:
            mediator.send(jsonRequest)
            return self.redirectToHome()
        except:
            self.clearCookies()
            return self.index(CustomHTTPError(403, server_constants.ERROR_SESSION_EXPIRED))
        finally:
            mediator.close()

    @cherrypy.expose
    def toggleForm(self, formState):
        formState = int(formState)
        form = self.forms[formState % 2]
        markup = self.view.create_form(form)
        return markup

    def tryLoginAndStartSession(self, email, password):
        jsonRequest = f'''
            {{
                "type": "{server_constants.TYPE_LOGIN_USER}",
                "email": "{email}",
                "password": "{password}"
            }}
        '''
        mediator = Mediator()
        mediator.create()
        try:
            data = mediator.send(jsonRequest).replace("'", "\"")
            responseData = json.loads(data)

            cherrypy.response.cookie["token"] = responseData["token"]
            cherrypy.response.cookie["user_id"] = responseData["user_id"]
            return self.redirectToHome()
        except:
            # I don't want to tell the user that just the password is wrong, therefore I'm telling him that either
            # the email or the password is wrong here
            raise CustomHTTPError(403, server_constants.ERROR_LOGIN_OR_PASSWORD_WRONG)
        finally:
            mediator.close()

    @cherrypy.expose
    def login(self, email, password):
        # Request the salt for the current user (if it exists).
        jsonRequest = f'''
            {{
                "type": "{server_constants.TYPE_GET_SALT}",
                "email": "{email}"
            }}
        '''
        mediator = Mediator()
        mediator.create()
        try:
            # Salt is found, user exists.
            # Create hashed password and try to login.
            salt = mediator.send(jsonRequest)
            hashedPassword = self.createSaltedPassword(password, salt)
        except InterruptedError:
            mediator.close()
            # Salt wasn't found, the user entered an invalid Email.
            # Consider to instead notify with server_constants.ERROR_LOGIN_OR_PASSWORD_WRONG
            raise CustomHTTPError(400, server_constants.ERROR_USER_DOES_NOT_EXIST)
        return self.tryLoginAndStartSession(email, hashedPassword)


cherrypy.engine.autoreload.unsubscribe()
# Static content config
static_config = {
    '/': {
        'tools.staticdir.root': sys.path[0],
        'tools.staticdir.on': True,
        'tools.staticdir.dir': './content'
    }
}

cherrypy.tree.mount(LoginHandler(), '/', static_config)
# suppress traceback-info
cherrypy.config.update({'request.show_tracebacks': False})
# Start server
cherrypy.engine.start()
cherrypy.engine.block()