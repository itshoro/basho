import cherrypy
import hashlib
import secrets

import socket


class LoginHandler:
    def __init__(self):
        self.dbSocket = socket.socket()
        self.dbSocket.connect(("127.0.0.1", 50007)) # TODO: Resolve via DNS
        self._TYPE_REGISTER_USER = "REGISTER"
        self._TYPE_LOGIN_USER = "LOGIN"

    @cherrypy.expose
    def register(self, email, password):
        salt = secrets.token_hex(8) # 16 character random string, ref: https://stackoverflow.com/a/50842164
        passHash = hashlib.sha1()
        passHash.update(password.encode("utf-8"))
        passHash.update(salt.encode("utf-8"))

        self.tryRegisterUser(email, passHash.hexdigest(), salt)


    def tryRegisterUser(self, email, password, salt):
        json = f'''
            {{
                "type": "{self._TYPE_REGISTER_USER}",
                "email": "{email}",
                "password": "{password}",
                "salt": "{salt}"
            }}
        '''.replace(" ", "")
        self.dbSocket.sendall(bytes(json, "utf-8"))

handler = LoginHandler()
handler.register("user@email.com", "password123")