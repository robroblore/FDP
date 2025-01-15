import socket
import threading
import main


class Client:
    def __init__(self, login):
        self.FORMAT = main.DEFAULT_FORMAT
        self.HEADERDATALEN = main.DEFAULT_HEADERDATALEN
        self.PORT = main.DEFAULT_PORT

        self.SERVER = None
        self.LOGIN = login

        self.isConnected = False

        # Create a socket object (AF_INET = IPv4, SOCK_STREAM = TCP)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.listener = None

    def connect(self):

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

    def receive(self):
        """
        Receive a message from the server

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
            case 0:
                # Debug message
                if data_length:
                    debug_message = self.client.recv(data_length).decode(self.FORMAT)
                    print(f"[DEBUG] {debug_message}")

            case 1:
                # Command
                if data_length:
                    Command = self.client.recv(data_length).decode(self.FORMAT)
                    print(f"[COMMAND] {Command}")

            case 2:
                # File
                file_name_len = int(self.client.recv(self.HEADERDATALEN).decode(self.FORMAT))
                file_name = self.client.recv(file_name_len).decode(self.FORMAT)
                print("[FILE] Receiving file: ", file_name)

            case _:
                # Invalid data type
                print("Invalid data type")
                return

        pass

    def listen(self):
        """
        Continuously listen for messages from the server
        """
        while self.isConnected:
            self.receive()
            pass
