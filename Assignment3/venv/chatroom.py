import select
import socket
import threading
import sys


class ServerTCP:
    def __init__(self, server_port):
        serverSocket = socket(AF_NET, SOCK_STREAM)
        addr = serverSocket.gethostbyname(socket.gethostbyname())
        serverSocket.bind((addr, server_port))
        self.clients = {}
        self.runEvent = threading.Event()
        self.handleEvent = threading.Event()
        runEvent.start()
        handleEvent.start()

    def accept_client(self):
        select.select(clients,

    def close_client(self, client_socket):
        pass

    def broadcast(self, client_socket_sent, message):
        pass

    def shutdown(self):
        pass

    def get_clients_number(self):
        pass

    def handle_client(self, client_socket):
        pass

    def run(self):
        pass


class ClientTCP:
    def __init__(self, client_name, server_port):
        pass
    def connect_server(self):
        pass
    def send(self, text):
        pass
    def receive(self):
        pass
    def run(self):
        pass


class ServerUDP:
    def __init__(self, server_port):
        pass
    def accept_client(self, client_addr, message):
        pass
    def close_client(self, client_addr):
        pass
    def broadcast(self):
        pass
    def shutdown(self):
        pass
    def get_clients_number(self):
        pass
    def run(self):
        pass


class ClientUDP:
    def __init__(self, client_name, server_port):
        pass
    def connect_server(self):
        pass
    def send(self, text):
        pass
    def receive(self):
        pass
    def run(self):
        pass