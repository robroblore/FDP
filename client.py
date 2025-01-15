import socket
import threading

class Client:
    def __init__(self, login):
        self.FORMAT = "utf-8"
        self.HEADERLEN = 64
        self.PORT = 6969

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

    def listen(self):
        """
        Continuously listen for messages from the server
        """
        while self.isConnected:
            #self.receive()
            pass