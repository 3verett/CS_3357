"""
Author: Everett Guyea
Date: 29-10-2025
"""

from socket import *
import sys
import os


def main():
    # set server hostname
    try:
        if len(sys.argv) < 2:
            print("Usage: ProxyServer.py <serverHost>")
            sys.exit(1)
        serverHost = sys.argv[1]
    except IndexError:
        print("Usage: ProxyServer.py <serverHost>")
        sys.exit(1)

    # set server port
    serverPort = 8888

    # check for cache directory
    if not os.path.exists("cache"):
        # create directory if DNE
        os.makedirs("cache")

    # set up TCP socket to listen for connections
    proxySocket = socket(AF_INET, SOCK_STREAM)
    proxySocket.bind((serverHost, serverPort))
    proxySocket.listen(5)

    print("Proxy server running... Press Ctrl+C to stop.")

    while True:
        print("Ready to serve...\n")
        clientSocket, clientAddress = proxySocket.accept()
        print(f"Received a connection from: {clientAddress}\n")

        handleRequest(clientSocket)


# Helper function to handle the client request
def handleRequest(clientSocket):
    request = clientSocket.recv(4096).decode()
    print(f"Raw request:\n{request}")

    # split request into method and address
    if "http://" not in request:
        clientSocket.close()
        return
    requestParts = request.split("http://")
    method = requestParts[0].strip()
    address = requestParts[1].strip()

    # Check for GET method
    if method != "GET":
        error = f"HTTP/1.0 405 Method Not Allowed\r\nContent-Type: text/plain\r\ncontent-Length: 22\r\n\r\n405 Method Not Allowed"
        clientSocket.sendall(error.encode())
        clientSocket.close()
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

    if port != 80:
        hostWPort = f"{host}_{port}"
    else:
        hostWPort = host

    print(f"Extracted:\nHost: {host}, Port:{port}, Path: {path}")

    filepath = "cache/" + hostWPort + path.replace("/", "_")
    if os.path.exists(filepath):
        print("<<< CACHE HIT >>>")
        with open(filepath, "rb") as cachedFile:
            data = cachedFile.read()
            clientSocket.sendall(data)
            print(f"Served from Local Cache: {filepath}")
    else:
        print("<<< CACHE MISS >>>")
        try:
            print("Connecting to Server...\n")
            # connect to server
            serverSocket = socket(AF_INET, SOCK_STREAM)
            serverSocket.connect((host, port))
            print(f"Connection successful to {host}:{port}")

            # GET request for server
            GETReq = f"GET {path} HTTP/1.0\r\nHost: {host}\r\nConnection: close\r\nUser-Agent: SimpleProxy/1.0\r\n\r\n"
            serverSocket.sendall(GETReq.encode())

            # response
            with open(filepath, "wb") as cacheFile:
                while True:
                    data = serverSocket.recv(4096)
                    if not data:
                        break
                    clientSocket.sendall(data)
                    cacheFile.write(data)

            size = os.path.getsize(filepath)
            print(f"Saved {size} bytes to cache")
            serverSocket.close()
        except Exception as e:
            print("Error fetching from origin:", e)
            error = "HTTP/1.0 502 Bad Gateway\r\nContent-Type: text/plain\r\nContent-Length: 15\r\n\r\n502 Bad Gateway"
            clientSocket.sendall(error.encode())
            clientSocket.close()
            serverSocket.close()

    clientSocket.close()


if __name__ == "__main__":
    main()
