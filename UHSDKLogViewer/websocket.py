# Requirement: pip3 install SimpleWebSocketServer
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import socket

# TODO: Get away from horrible Global 'clients' !
clients = []
class SimpleWSServer(WebSocket):
    def handleConnected(self):
        clients.append(self)

    def handleClose(self):
        clients.remove(self)

def socketIsOpen():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("", 9000))

    # Checking if Server Port is Open...
    if result == 0:
       print("Port 9000 is open")
       return True
    else:
       print("Port 9000 is not open")
       return False

def createWebSocketServer():
    clients = []
    return SimpleWebSocketServer("", 9000, SimpleWSServer, selectInterval=(1000.0 / 15) / 1000)

def get_clients():
    return clients