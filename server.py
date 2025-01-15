import socket
import threading
import main


class Server:
    def __init__(self):
        self.FORMAT = main.DEFAULT_FORMAT
        self.HEADERDATALEN = main.DEFAULT_HEADERDATALEN
        self.PORT = main.DEFAULT_PORT
        self.DataType = main.DataType

        self.SERVER_IP = socket.gethostbyname(socket.gethostname())
        self.ADDR = (self.SERVER_IP, main.DEFAULT_PORT)

        # Create a socket object (AF_INET = IPv4, SOCK_STREAM = TCP)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the port 6969
        self.server.bind(self.ADDR)

        self.CLIENTS = dict()

    # TODO: Use threading for file transfer so app doesnt freeze
    # TODO: Check file hash to ensure file integrity
    def handle_client(self, conn):
        # Get client name
        login = conn.recv(64).decode(self.FORMAT)
        self.CLIENTS[login] = conn
        print(f"{login} has connected to the server from {conn.getpeername()}")

        while True:
            try:
                data_type = int(conn.recv(1).decode(self.FORMAT))

                if data_type == self.DataType.DISCONNECT:
                    break

                data_length = int(conn.recv(self.HEADERDATALEN).decode(self.FORMAT))

                match data_type:
                    case self.DataType.DEBUG:
                        # Debug message
                        if data_length:
                            debug_message = conn.recv(data_length).decode(self.FORMAT)
                            print(f"[DEBUG] {debug_message}")

                    case self.DataType.COMMAND:
                        # Command
                        if data_length:
                            command = conn.recv(data_length).decode(self.FORMAT)
                            print(f"[COMMAND] {command}")

                    case self.DataType.FILE:
                        # File
                        file_name_len = int(conn.recv(self.HEADERDATALEN).decode(self.FORMAT))
                        file_name = conn.recv(file_name_len).decode(self.FORMAT)
                        print("[FILE] Receiving file: ", file_name)

                        # TODO: RECEIVE FILES

                    case _:
                        # Invalid data type
                        print("Invalid data type")
                        return
            except Exception as err:
                print(f"Unexpected {err=}, {type(err)=}")
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
