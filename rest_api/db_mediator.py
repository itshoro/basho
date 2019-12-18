from socket import socket

class Mediator:
    def __init__(self):
        self.socket = socket()

    def create(self, url = ("127.0.0.1", 50007)):
        self.socket.connect(url)

    def close(self):
        self.socket.close()

    def send(self, data, recv_length = 1024):
        self.socket.sendall(data)
        data = self.socket.recv(recv_length)
        
        if data:
            return data.decode("utf-8")
        else:
            self.socket.close()