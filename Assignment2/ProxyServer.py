"""
Author: Everett Guyea
Date: 29-10-2025
"""

from socket import *
import sys
import os


def main():
    # set server hostname and port
    serverHost = sys.argv[1]
    serverPort = 8888

    # check for cache directory
    if not os.path.exists("cache"):
        # create directory if DNE
        os.makedirs("cache")

    # set up TCP socket to listen for connections
    proxySocket = socket(AF_INET, SOCK_STREAM)
    proxySocket.bind((serverHost, serverPort))
    proxySocket.listen(5)

    print("Proxy server running... Press Ctrl+C to stop.\nReady to serve...")

    while True:
        clientSocket, clientAddress = proxySocket.accept()
        print(f"Received a connection from: {clientAddress}")

        handleRequest(clientSocket)


# Helper function to handle the client request
def handleRequest(clientSocket):
    request = clientSocket.recv(4096).decode()
    print(f"Raw request:\n{request}")

    # split request into method and address
    request.split("http://")
    method = request[0].strip()
    address = request[1].strip()

    # Check for GET method
    if method != "GET":
        print(f"HTTP/1.0 405 Method Not Allowed\nContent-Type: text/plain\ncontent-Length: {len(request)}\n405 Method Not Allowed")
        return

    # remove HTTP ver.
    address = address.split()[0]

    # split host:port from path by splitting at the first '/'
    address = address.split("/", 1)
    hostPort = address[0]
    path = "/" + address[1] if len(address) > 1 else "/"

    # check for specified port #
    if ":" in hostPort:
        host, port = hostPort.split(":")
        port = int(port)
    else:
        host = hostPort
        port = 80

    print(f"Host: {host}\nPort: {port}\nPath: {path}")
