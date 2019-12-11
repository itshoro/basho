import cherrypy
import hashlib
import secrets

import sys

import socket
import json

# Because we send the error messages as plain text instead of a full blown error page.
class CustomHTTPError(cherrypy.HTTPError):
    def __init__(self, status, message):
        super().__init__(status, message)

    def set_response(self):
        super().set_response()
        response = cherrypy.serving.response
        response.headers["Content-Length"] = len(self._message.encode("utf-8"))
        response.body = self._message.encode("utf-8")

class LoginHandler:
    def __init__(self):
        self._TYPE_REGISTER_USER = "REGISTER"
        self._TYPE_LOGIN_USER = "LOGIN"
        self._TYPE_GET_SALT = "GET_SALT"
        self._TYPE_VALIDATE_SESSION = "VALIDATE_SESSION"

        self._ERROR_LOGIN_OR_PASSWORD_WRONG = "Your Email or password is invalid."
        self._ERROR_SESSION_EXPIRED = "Your session is expired, please login again."
        self._ERROR_USER_ALREADY_EXISTS = "An account with that Email already exists."
        self._ERROR_USER_DOES_NOT_EXIST = "An account with that Email does not exist."

    @cherrypy.expose
    def index(self):
        # Check for a session cookie.
        if (len(cherrypy.request.cookie) == 2 and cherrypy.request.cookie["sessionToken"]):
            return self.tryValidateAndRecoverSession()
        else:
            return open("login.html")

    @cherrypy.expose
    def register(self, email, password):
        self.dbSocket = socket.socket()
        self.dbSocket.connect(("127.0.0.1", 50007)) # TODO: Resolve via DNS
        salt = secrets.token_hex(8) # 16 character random string, ref: https://stackoverflow.com/a/50842164
        
        hashedPassword = self.createSaltedPassword(password, salt)
        jsonRequest = f'''
            {{
                "type": "{self._TYPE_REGISTER_USER}",
                "email": "{email}",
                "password": "{hashedPassword}",
                "salt": "{salt}"
            }}
        '''
        self.dbSocket.sendall(bytes(jsonRequest, "utf-8")) # TODO: Handle response
        data = self.dbSocket.recv(1024)

        id = -1
        if data:
            id = data.decode("utf-8")

        if id == -1:
            raise CustomHTTPError(400, self._ERROR_USER_ALREADY_EXISTS)
        self.dbSocket.close()

    def redirectToHome(self):
        return open("index.html")

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
            # TODO: Open Login page and somehow trigger the js for an error
            raise CustomHTTPError(403, self._ERROR_SESSION_EXPIRED)

        self.dbSocket = socket.socket()
        self.dbSocket.connect(("127.0.0.1", 50007)) # TODO: Resolve via DNS

        jsonRequest = f'''
            {{
                "type": "{self._TYPE_VALIDATE_SESSION}",
                "token": "{cherrypy.request.cookie["sessionToken"].value}",
                "user_id": "{cherrypy.request.cookie["user_id"].value}"
            }}
        '''
        self.dbSocket.sendall(bytes(jsonRequest, "utf-8"))
        data = self.dbSocket.recv(1024)

        if data:
            # Token is valid, let server handle the new expiry time stamp.
            # Consider to return the new expiry date as argument to the cookie.
            self.dbSocket.close()
            return self.redirectToHome()
        else:
            self.dbSocket.close()
            self.clearCookies()
            # TODO: Open Login page and somehow trigger the js for an error
            raise CustomHTTPError(403, self._ERROR_SESSION_EXPIRED)

    def tryLoginAndStartSession(self, email, password):
        jsonRequest = f'''
            {{
                "type": "{self._TYPE_LOGIN_USER}",
                "email": "{email}",
                "password": "{password}"
            }}
        '''

        self.dbSocket.sendall(bytes(jsonRequest, "utf-8"))
        data = self.dbSocket.recv(1024)

        if data:
            jsonResponse = data.decode("utf-8").replace("'", "\"")
            responseData = json.loads(jsonResponse)

            cherrypy.response.cookie["sessionToken"] = responseData["sessionToken"]
            cherrypy.response.cookie["user_id"] = responseData["user_id"]

            self.dbSocket.close()
            self.redirectToHome()
        else:
            self.dbSocket.close()
            # I don't want to tell the user that just the password is wrong, therefore I'm telling him that either
            # the email or the password is wrong here.
            raise CustomHTTPError(403, self._ERROR_LOGIN_OR_PASSWORD_WRONG)

    @cherrypy.expose
    def login(self, email, password):
        # Request the salt for the current user (if it exists).
        jsonRequest = f'''
            {{
                "type": "{self._TYPE_GET_SALT}",
                "email": "{email}"
            }}
        '''
        self.dbSocket = socket.socket()
        self.dbSocket.connect(("127.0.0.1", 50007)) # TODO: Resolve via DNS

        self.dbSocket.sendall(bytes(jsonRequest, "utf-8"))
        data = self.dbSocket.recv(1024)

        if data:
            # Salt is found, user exists.
            # Create hashed password and try to login.
            salt = data.decode("utf-8")
            hashedPassword = self.createSaltedPassword(password, salt)

            self.tryLoginAndStartSession(email, hashedPassword)
        else:
            # Salt wasn't found, the user entered an invalid Email.
            # Consider to instead notify with self._ERROR_LOGIN_OR_PASSWORD_WRONG
            raise CustomHTTPError(400, self._ERROR_USER_DOES_NOT_EXIST)


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