import socket

class UDPSender :

    def __init__(self,ip,port) :
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1)
        self.ip = ip
        self.port = port

    def send(self,data) :
        self.socket.sendto(str.encode(data),(self.ip,self.port))
