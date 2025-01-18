"""
FDP - File Delivery Protocol
"""
import socket

import server
import client
from enum import IntEnum
import threading

from tools import DataType

# FORMAT = The format (encryption) of the message to be received
DEFAULT_FORMAT = "utf-8"

# HEADERLEN = Information about the message to be received (in this case,
# the length of the message)
DEFAULT_HEADERDATALEN = 64

DEFAULT_PORT = 6942  # Default port number for the server

DEFAULT_SERVER_FILES_SAVE_PATH = "server_files"

if __name__ == "__main__":
    local = None
    print("FDP - File Delivery Protocol")
    print("1. Host Server")
    print("2. Connect to Server")
    isHost = not (int(input("Enter your choice: ")) - 1)

    def start_server(sv):
        sv.start()

    if isHost:
        server = server.Server()
        thread = threading.Thread(target=start_server, args=(server,), daemon=True)
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

    local_client = client.Client(login)
    if not isHost:
        server_ip = input("Enter the server IP (10.xxx.xxx.xxx): ")
        local_client.connect_to_server(server_ip)
    else:
        local_client.connect_to_server(socket.gethostbyname(socket.gethostname()))

    while True:
        print("1. Send debug")
        print("2. Send command")
        print("3. Send file")
        print("4. Exit")

        choice = int(input("Enter your choice: "))

        match choice:
            case 1:
                local_client.send(DataType.DEBUG, input("Enter debug message: "))
            case 2:
                local_client.send(DataType.COMMAND, input("Enter command: "))
            case 3:
                local_client.send(DataType.UPLOAD_FILE, input("Enter file path: "))
            case 4:
                local_client.send(DataType.DISCONNECT)
                break
            case _:
                print("Invalid choice")
                continue
