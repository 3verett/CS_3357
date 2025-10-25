"""
Author: Everett Guyea
Date: 25-10-2025
"""

import time
from socket import *
import sys


def main():
    # Get hostname and port from arguments
    serverHost = sys.argv[1]
    serverPort = int(sys.argv[2])
    address = (serverHost, serverPort)

    # Create socket and set timeout
    clientSock = socket(AF_INET, SOCK_DGRAM)
    clientSock.settimeout(1)

    for seqNum in range(1, 11):
        # create ping message
        sentTime = time.time()
        message = f"Ping {seqNum} {sentTime}"

        try:
            # send ping
            clientSock.sendto(message.encode(), address)

            # reply + calc rtt
            data, server = clientSock.recvfrom(1024)
            recvTime = time.time()
            rtt = recvTime - sentTime

            print(f"Reply from {serverHost}: PING {seqNum} {time}\nRTT: {rtt}")
        except timeout:
            print(f"Request timed out.")

    clientSock.close()


if __name__ == "__main__":
    main()
