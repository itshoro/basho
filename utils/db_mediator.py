from socket import socket

class Mediator:
    def __init__(self):
        self.socket = socket()

    def create(self, url = ("127.0.0.1", 50007)):
        self.socket.connect(url)

    def close(self):
        self.socket.close()

    def send(self, data:str, encoding = "utf-8", recv_length = 1024):
        data = bytes(data, encoding)
        self.socket.sendall(data)
        data = self.socket.recv(recv_length)
        
        if data:
            return data.decode(encoding)
        else:
            self.socket.close()
            raise InterruptedError()