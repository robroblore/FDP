"""
FDP - File Delivery Protocol
"""

import server
import client
from enum import IntEnum
import threading

# FORMAT = The format (encryption) of the message to be received
DEFAULT_FORMAT = "utf-8"

# HEADERLEN = Information about the message to be received (in this case,
# the length of the message)
DEFAULT_HEADERDATALEN = 64

DEFAULT_PORT = 6969  # Default port number for the server


class DataType(IntEnum):
    DEBUG = 0
    COMMAND = 1
    FILE = 2


if __name__ == "__main__":
    local = None
    print("FDP - File Delivery Protocol")
    print("1. Host Server")
    print("2. Connect to Server")
    isHost = not (int(input("Enter your choice: ")) - 1)
    # if isHost == 1:
    #     local = server.Server()
    #     local.start()
    # elif isHost == 0:
    #     login = ""
    #     while not login:
    #         login = input("Enter your username: ")
    #         if login.isspace():
    #             print("Username cannot be empty")
    #             login = ""
    #         elif not login.isalnum():
    #             print("Username must only contain alphanumeric characters")
    #             login = ""
    #         elif len(login) > 64:
    #             print("Username must be less than 64 characters")
    #             login = ""
    #     local = client.Client(login, isHost)
    #     local.connect()
    # else:
    #     print("Invalid choice")

    def start_server(sv):
        sv.start()

    if isHost:
        server = server.Server()
        thread = threading.Thread(target=start_server, args=(server,))
        thread.start()

    login = ""
    while not login:
        login = input("Enter your username: ")
        if login.isspace():
            print("Username cannot be empty")
            login = ""
        elif not login.isalnum():
            print("Username must only contain alphanumeric characters")
            login = ""
        elif len(login) > 64:
            print("Username must be less than 64 characters")
            login = ""

    local_client = client.Client(login, isHost)
    local_client.connect()
