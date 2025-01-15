import socket
import threading
import main
import os


class Client:

    def __init__(self, login, isHost):
        self.FORMAT = main.DEFAULT_FORMAT
        self.HEADERDATALEN = main.DEFAULT_HEADERDATALEN
        self.PORT = main.DEFAULT_PORT
        self.DataType = main.DataType
        self.FILE_CHUNK_SIZE = 1024

        self.SERVER = None
        self.LOGIN = login
        self.isHost = isHost

        self.isConnected = False

        # Create a socket object (AF_INET = IPv4, SOCK_STREAM = TCP)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.listener = None

    def connect(self):

        if self.isHost:
            self.SERVER = socket.gethostbyname(socket.gethostname())
        else:
            self.SERVER = input("Enter the server IP (10.xxx.xxx.xxx): ")

        try:
            # Connect to the server
            self.client.connect((self.SERVER, self.PORT))
            print(f"Connected to {self.SERVER} on port {self.PORT}")
            self.isConnected = True
        except Exception as err:
            print("Connection failed")
            print(f"Unexpected {err=}, {type(err)=}")
            return

        self.client.send(self.LOGIN.encode(self.FORMAT))

        # Listen for messages from the server and be able to send messages to the server at the same time using
        # threading
        self.listener = threading.Thread(target=self.listen)
        self.listener.start()

    def send(self, data_type: int, data: str):
        """
        Sent data to the server

        Persistent header information:
            - Data type {0: Debug, 1: Command, 2: File}
            - Data length

        Optional header information (for files):
            - File name size
            - File name
        """

        if data_type == self.DataType.FILE:
            if not os.path.exists(data):
                print("File does not exist")
                return

            data_size = os.path.getsize(data)
        else:
            data_size = len(data)

        self.client.send(str(data_type).encode(self.FORMAT))

        data_size_info = str(data_size).encode(self.FORMAT)
        data_size_info += b' ' * (self.HEADERDATALEN - len(data_size_info))

        match data_type:
            case self.DataType.DEBUG:
                # Debug message
                data = data.encode(self.FORMAT)
                self.client.send(data_size_info)
                self.client.send(data)

            case self.DataType.COMMAND:
                # Command
                data = data.encode(self.FORMAT)
                self.client.send(data_size_info)
                self.client.send(data)

            case self.DataType.FILE:
                # File -> data = file path
                # Could use socket.sendfile() but where's the fun in that?
                self.client.send(data_size_info)
                file_name = data.split("//")[-1]
                self.client.send(str(len(file_name)).encode(self.FORMAT))
                self.client.send(file_name.encode(self.FORMAT))

                print("[FILE] Started sending file: ", file_name)

                chunks = data_size // self.FILE_CHUNK_SIZE
                remaining_data = data_size % self.FILE_CHUNK_SIZE
                print("[DEBUG] File size: ", data_size)
                print("[DEBUG] Number of chunks: ", data_size)
                print("[DEBUG] Remaining data: ", remaining_data)

                counter = 0
                with open(data, "rb") as file:
                    for size in [chunks * self.FILE_CHUNK_SIZE, remaining_data]:
                        print(f"Sent {counter} chunk(s) out of {chunks + 1} ({(chunks+1) / counter})")
                        file_data = file.read(size)
                        if not file_data:
                            break
                        self.client.send(file_data)
                        counter += 1

            case self.DataType.DISCONNECT:
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
            - Data type {0: Debug, 1: Command, 2: File}
            - Data length

        Optional header information (for files):
            - File name size
            - File name
        """

        try:
            data_type = int(self.client.recv(1).decode(self.FORMAT))
        except:
            return

        data_length = int(self.client.recv(self.HEADERDATALEN).decode(self.FORMAT))

        match data_type:
            case self.DataType.DEBUG:
                # Debug message
                if data_length:
                    debug_message = self.client.recv(data_length).decode(self.FORMAT)
                    print(f"[DEBUG] {debug_message}")

            case self.DataType.COMMAND:
                # Command
                if data_length:
                    command = self.client.recv(data_length).decode(self.FORMAT)
                    print(f"[COMMAND] {command}")

            case self.DataType.FILE:
                # File
                file_name_len = int(self.client.recv(self.HEADERDATALEN).decode(self.FORMAT))
                file_name = self.client.recv(file_name_len).decode(self.FORMAT)
                print("[FILE] Receiving file: ", file_name)

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
