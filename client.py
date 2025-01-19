import json
import random
import socket
import threading

from PySide6.QtCore import QObject
from qtpy.QtCore import Signal

import main
import os

from tools import receive_data, send_data, DataType, send_file, receive_file


# Inherit from QObject to be able to use signals
class Client(QObject):
    files_info_received = Signal(list)

    def __init__(self):
        super().__init__()
        self.FORMAT = main.DEFAULT_FORMAT
        self.HEADERDATALEN = main.DEFAULT_HEADERDATALEN
        self.PORT = main.DEFAULT_PORT
        self.FILE_CHUNK_SIZE = 1024

        self.SERVER = None
        self.LOGIN = None

        self.isConnected = False

        # Create a socket object (AF_INET = IPv4, SOCK_STREAM = TCP)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Dictionary to store the file paths to save files, with the hash of the file path as the key
        # Used to know which file the server is sending us
        self.paths_to_save_files = {}

        self.listener = None

    def connect_to_server(self, login, server_ip):
        self.SERVER = server_ip
        self.LOGIN = login

        try:
            # Connect to the server
            self.client.connect((self.SERVER, self.PORT))
            print(f"Connected to {self.SERVER} on port {self.PORT}")
            self.isConnected = True
        except Exception as err:
            print("Connection failed")
            print(f"Unexpected {err=}, {type(err)=}")
            return False

        send_data(self.client, self.LOGIN.encode(self.FORMAT), 64)
        result = receive_data(self.client, 1)

        if not result:
            print("Connection closed")
            self.isConnected = False
            self.client.close()
            return False

        # Listen for messages from the server and be able to send messages to the server at the same time using
        # threading
        self.listener = threading.Thread(target=self.listen, daemon=True)
        self.listener.start()
        return True

    def send(self, data_type: int, data: str = ""):
        """
        Sent data to the server

        Persistent header information:
            - Data type {0: Debug, 1: Command, 2: Upload file, 3: Download file, 4: Files info, 5: Delete file, 6: Disconnect}
        """

        if not self.isConnected:
            print("Not connected to the server")
            return

        send_data(self.client, str(data_type).encode(self.FORMAT), len(str(data_type)))

        match data_type:
            case DataType.DEBUG:
                # Debug message
                data = data.encode(self.FORMAT)
                data_size = str(len(data)).encode(self.FORMAT)

                send_data(self.client, data_size, self.HEADERDATALEN)
                send_data(self.client, data, len(data))

            case DataType.COMMAND:
                # Command
                data = data.encode(self.FORMAT)
                data_size = str(len(data)).encode(self.FORMAT)

                send_data(self.client, data_size, self.HEADERDATALEN)
                send_data(self.client, data, len(data))

            case DataType.UPLOAD_FILE:
                # Upload file -> data = file path
                print("[DEBUG] Uploading file")

                file_name = os.path.basename(data).encode(self.FORMAT)
                file_name_size = str(len(file_name)).encode(self.FORMAT)

                send_data(self.client, file_name_size, self.HEADERDATALEN)
                send_data(self.client, file_name, len(file_name))

                send_file(self.client, data, self.HEADERDATALEN, self.FORMAT, self.FILE_CHUNK_SIZE)

            case DataType.FILES_INFO:
                # Files info
                # Send no data as we want to signal the server to send us the files info
                print("[DEBUG] Requesting files info")

            case DataType.DELETE_FILE:
                # Delete file -> data = file name
                print("[DEBUG] Deleting file")
                file_name = data.encode(self.FORMAT)
                file_name_size = str(len(file_name)).encode(self.FORMAT)

                send_data(self.client, file_name_size, self.HEADERDATALEN)
                send_data(self.client, file_name, len(file_name))

            case DataType.DISCONNECT:
                # Disconnect
                self.isConnected = False
                self.client.close()

            case _:
                # Invalid data type
                print("Invalid data type")
                return

    def receive(self):
        """
        Receive data from the server

        Persistent header information:
            - Data type {0: Debug, 1: Command, 2: Upload file, 3: Download file, 4: Files info, 5: Delete file, 6: Disconnect}
        """

        data_received = receive_data(self.client, 1)
        if not data_received:
            print("Connection closed")
            self.isConnected = False
            self.client.close()
            return
        data_type = int(data_received.decode(self.FORMAT))

        match data_type:
            case DataType.DEBUG:
                # Debug message
                data_length = int(receive_data(self.client, self.HEADERDATALEN).decode(self.FORMAT))
                if data_length:
                    debug_message = receive_data(self.client, data_length).decode(self.FORMAT)
                    print(f"[DEBUG] {debug_message}")

            case DataType.COMMAND:
                # Command
                data_length = int(receive_data(self.client, self.HEADERDATALEN).decode(self.FORMAT))
                if data_length:
                    command = receive_data(self.client, data_length).decode(self.FORMAT)
                    print(f"[COMMAND] {command}")

            case DataType.DOWNLOAD_FILE:
                # File
                print("[DEBUG] Downloading file")
                file_path_hash_size = int(receive_data(self.client, self.HEADERDATALEN).decode(self.FORMAT))
                file_path_hash = receive_data(self.client, file_path_hash_size).decode(self.FORMAT)

                receive_file(self.client, self.HEADERDATALEN, self.FORMAT, self.FILE_CHUNK_SIZE, self.paths_to_save_files[str(file_path_hash)])
                del self.paths_to_save_files[str(file_path_hash)]

            case DataType.FILES_INFO:
                # Files info
                print("[DEBUG] Receiving files info")
                files_info_size = int(receive_data(self.client, self.HEADERDATALEN).decode(self.FORMAT))
                files_info = receive_data(self.client, files_info_size).decode(self.FORMAT)
                self.files_info_received.emit(json.loads(files_info))

            case _:
                # Invalid data type
                print("Invalid data type")
                return

    def listen(self):
        """
        Continuously listen for messages from the server
        """
        while self.isConnected:
            self.receive()

    def download_file(self, file_name, file_path):
        """
        Download a file from the server
        Send a hash of the file path to the server to later know which file the server is sending us
        Add a random number in the hash to allow for multiple files with the same name to be downloaded
        """

        send_data(self.client, str(DataType.DOWNLOAD_FILE).encode(self.FORMAT), len(str(DataType.DOWNLOAD_FILE)))

        file_name = file_name.encode(self.FORMAT)
        file_name_size = str(len(file_name)).encode(self.FORMAT)

        send_data(self.client, file_name_size, self.HEADERDATALEN)
        send_data(self.client, file_name, len(file_name))

        file_path_hash = hash(file_path + random.randint(0, 1000000000))
        self.paths_to_save_files[str(file_path_hash)] = file_path

        file_path_hash = str(file_path_hash).encode(self.FORMAT)
        file_path_hash_size = str(len(file_path_hash)).encode(self.FORMAT)

        send_data(self.client, file_path_hash_size, self.HEADERDATALEN)
        send_data(self.client, file_path_hash, len(file_path_hash))
