import cherrypy
import hashlib
import secrets

import socket


class LoginHandler:
    def __init__(self):
        self._TYPE_REGISTER_USER = "REGISTER"
        self._TYPE_LOGIN_USER = "LOGIN"
        self._TYPE_GET_SALT = "GET_SALT"

    @cherrypy.expose
    def register(self, email, password):
        self.dbSocket = socket.socket()
        self.dbSocket.connect(("127.0.0.1", 50007)) # TODO: Resolve via DNS
        salt = secrets.token_hex(8) # 16 character random string, ref: https://stackoverflow.com/a/50842164
        passHash = hashlib.sha1()
        passHash.update(password.encode("utf-8"))
        passHash.update(salt.encode("utf-8"))

        self.tryRegisterUser(email, passHash.hexdigest(), salt)
        self.dbSocket.close()

    @cherrypy.expose
    def login(self, email, password):
        self.dbSocket = socket.socket()
        self.dbSocket.connect(("127.0.0.1", 50007)) # TODO: Resolve via DNS
        json = f'''
            {{
                "type": "{self._TYPE_GET_SALT}",
                "email": "{email}"
            }}
        '''
        self.dbSocket.sendall(bytes(json, "utf-8"))
        data = self.dbSocket.recv(1024)

        if data:
            salt = data.decode("utf-8")

            passHash = hashlib.sha1()
            passHash.update(password.encode("utf-8"))
            passHash.update(salt.encode("utf-8"))
            json = f'''
                {{
                    "type": "{self._TYPE_LOGIN_USER}",
                    "email": "{email}",
                    "password": "{passHash.hexdigest()}"
                }}
            '''
            self.dbSocket.sendall(bytes(json, "utf-8"))
            data = self.dbSocket.recv(1024)
            print(data)
            self.dbSocket.close()
        else:
            self.dbSocket.close()
            return False # Login fails


    def tryRegisterUser(self, email, password, salt):
        json = f'''
            {{
                "type": "{self._TYPE_REGISTER_USER}",
                "email": "{email}",
                "password": "{password}",
                "salt": "{salt}"
            }}
        '''.replace(" ", "")
        self.dbSocket.sendall(bytes(json, "utf-8")) # TODO: Handle response

handler = LoginHandler()
# handler.register("user@email.com", "password123")
handler.login("user@email.com", "password123")