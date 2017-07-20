import socket

class TCPSocket :

    def __init__(self,ip,port) :
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((ip,port))
        self.socket.listen(1)
        self.wait()

    def wait(self) :
        self.client,addr = self.socket.accept()

    def send(self,data) :
        if self.client is not None :
            self.client.send(data)
