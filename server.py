import socket

BUFSIZE = 1024


class JudgeServer:
    def __init__(self, ip):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind(ip)

    def connect(self):
        pass

    def run(self):
        while True:
            data, client_addr = self.server.recvfrom(BUFSIZE)
