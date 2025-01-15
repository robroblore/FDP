import socket
import threading
import main


class Server:
    def __init__(self):
        self.FORMAT = main.DEFAULT_FORMAT
        self.HEADERDATALEN = main.DEFAULT_HEADERDATALEN
        self.PORT = main.DEFAULT_PORT

        self.SERVER_IP = socket.gethostbyname(socket.gethostname())
        self.ADDR = (self.SERVER_IP, main.DEFAULT_PORT)

        # Create a socket object (AF_INET = IPv4, SOCK_STREAM = TCP)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the port 6969
        self.server.bind(self.ADDR)

        self.CLIENTS = dict()

    def handle_client(self, conn):
        # Get client name
        login = conn.recv(64).decode(self.FORMAT)
        self.CLIENTS[login] = conn
        print(f"{login} has connected to the server from {conn.getpeername()}")

        while True:
            try:
                pass
            except:
                break

        print(f"{login} has disconnected from the server")
        del self.CLIENTS[login]
        conn.close()

    def start(self):
        # Listen for incoming connections
        self.server.listen()
        print(f"Server is listening on {self.SERVER_IP}:{self.PORT}")
        while True:
            # Accept the connection
            conn, addr = self.server.accept()
            # Print the address of the connected client
            print(f"Connection from {addr} has been established.")
            # Start a new thread to handle the connection
            thread = threading.Thread(target=self.handle_client, args=(conn,))
            thread.start()
