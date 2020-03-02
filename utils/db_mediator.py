from socket import socket, error

class Mediator:
    def __init__(self, urls = [("127.0.0.1", 50007)]):
        self.validUrls = urls
        self.connected = False

    def create(self):
        self.socket = socket()

        for i in range(0, len(self.validUrls)):
            try:
                self.socket.connect(self.validUrls[i])
                self.connected = True
                break
            except error:
                print(f"Can't reach {self.validUrls[i]}")

        if not self.connected:
            raise error("No mediator is available")

    def close(self):
        self.socket.close()

    def send(self, data:str, encoding = "utf-8", recv_length = 1024):
        data = bytes(data, encoding)
        self.socket.sendall(data)
        data = self.socket.recv(recv_length)
        
        if data:
            return data.decode("utf-8")
        else:
            self.socket.close()
            raise InterruptedError()