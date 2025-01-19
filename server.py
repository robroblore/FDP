import json
import os
import selectors
import socket
import types

import main
from tools import receive_data, send_data, DataType, receive_file, send_file


class Server:
    def __init__(self):
        self.FORMAT = main.DEFAULT_FORMAT
        self.HEADERDATALEN = main.DEFAULT_HEADERDATALEN
        self.PORT = main.DEFAULT_PORT
        self.SERVER_FILES_SAVE_PATH = main.DEFAULT_SERVER_FILES_SAVE_PATH
        self.FILE_CHUNK_SIZE = 1024

        self.SERVER_IP = socket.gethostbyname(socket.gethostname())

        self.CLIENTS = dict()
        self.selector = selectors.DefaultSelector()

    # TODO: Use threading for file transfer so app doesnt freeze
    # TODO: Check file hash to ensure file integrity
    def handle_client(self, key: selectors.SelectorKey, mask: int):
        conn: socket.socket = key.fileobj

        if mask & selectors.EVENT_READ:
            data_type = int(receive_data(conn, 1).decode(self.FORMAT))

            if data_type == DataType.DISCONNECT:
                self.close_client(conn)

            match data_type:
                case DataType.DEBUG:
                    # Debug message
                    data_length = int(receive_data(conn, self.HEADERDATALEN).decode(self.FORMAT))
                    if data_length:
                        debug_message = receive_data(conn, data_length).decode(self.FORMAT)
                        print(f"[DEBUG] {debug_message}")

                case DataType.COMMAND:
                    # Command
                    data_length = int(receive_data(conn, self.HEADERDATALEN).decode(self.FORMAT))
                    if data_length:
                        command = receive_data(conn, data_length).decode(self.FORMAT)
                        print(f"[COMMAND] {command}")

                case DataType.UPLOAD_FILE:
                    print("[DEBUG] Receiving file")

                    file_name_size = int(receive_data(conn, self.HEADERDATALEN).decode(self.FORMAT))
                    file_name = receive_data(conn, file_name_size).decode(self.FORMAT)

                    if not os.path.exists(self.SERVER_FILES_SAVE_PATH):
                        os.makedirs(self.SERVER_FILES_SAVE_PATH)
                    file_path = os.path.join(self.SERVER_FILES_SAVE_PATH, file_name)

                    receive_file(conn, self.HEADERDATALEN, self.FORMAT, self.FILE_CHUNK_SIZE, file_path)
                    self.send_files_info()

                case DataType.DOWNLOAD_FILE:
                    # Receive a hash of the file path to send it back to the client to tell it which file is being sent
                    file_name_size = int(receive_data(conn, self.HEADERDATALEN).decode(self.FORMAT))
                    file_name = receive_data(conn, file_name_size).decode(self.FORMAT)

                    file_path_hash_size = int(receive_data(conn, self.HEADERDATALEN).decode(self.FORMAT))
                    file_path_hash = receive_data(conn, file_path_hash_size).decode(self.FORMAT)

                    send_data(conn, str(DataType.DOWNLOAD_FILE).encode(self.FORMAT), 1)
                    send_data(conn, str(file_path_hash_size).encode(self.FORMAT), self.HEADERDATALEN)
                    send_data(conn, file_path_hash.encode(self.FORMAT), len(file_path_hash))

                    file_path = os.path.join(self.SERVER_FILES_SAVE_PATH, file_name)
                    send_file(conn, file_path, self.HEADERDATALEN, self.FORMAT, self.FILE_CHUNK_SIZE)

                case DataType.FILES_INFO:
                    self.send_files_info(conn)

                case DataType.DELETE_FILE:
                    file_name_size = int(receive_data(conn, self.HEADERDATALEN).decode(self.FORMAT))
                    file_name = receive_data(conn, file_name_size).decode(self.FORMAT)
                    file_path = os.path.join(self.SERVER_FILES_SAVE_PATH, file_name)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"[DEBUG] Deleting file: {file_name}")
                        self.send_files_info()
                    else:
                        print(f"[DEBUG] File {file_name} does not exist")

                case _:
                    # Invalid data type
                    print("Invalid data type")
                    return

    def send_files_info(self, conn=None):
        """
        Sends information about the files stored on the server to the clients.
        """

        print("[DEBUG] Sending files info")
        data = str(self.get_server_files_info()).encode(self.FORMAT)
        data_size = len(data)
        data_size_info = str(data_size).encode(self.FORMAT)

        if conn is not None:
            send_data(conn, str(DataType.FILES_INFO).encode(self.FORMAT), 1)
            send_data(conn, data_size_info, self.HEADERDATALEN)
            send_data(conn, data, data_size)
        else:
            for client in self.CLIENTS.values():
                send_data(client, str(DataType.FILES_INFO).encode(self.FORMAT), 1)
                send_data(client, data_size_info, self.HEADERDATALEN)
                send_data(client, data, data_size)

    def get_server_files_info(self):
        """
        Returns a list of dictionaries containing information about the files stored on the server.
        """

        files_info = []
        if os.path.exists(self.SERVER_FILES_SAVE_PATH):
            for file_name in os.listdir(self.SERVER_FILES_SAVE_PATH):
                file_path = os.path.join(self.SERVER_FILES_SAVE_PATH, file_name)
                file_size = os.path.getsize(file_path)
                files_info.append({
                    "file_name": file_name,
                    "file_size": file_size
                })
        return json.dumps(files_info)

    def start(self):
        """
        Starts the server and listens for incoming connections.
        """

        print(f"Starting server on {self.SERVER_IP}:{self.PORT}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener_socket:
            listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener_socket.bind((self.SERVER_IP, self.PORT))
            listener_socket.listen()
            print(f"Listening on {self.SERVER_IP}:{self.PORT}")
            self.selector.register(listener_socket, selectors.EVENT_READ)

            while True:
                events = self.selector.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_connection(key.fileobj)
                    else:
                        try:
                            self.handle_client(key, mask)
                        except ConnectionResetError:
                            self.close_client(key.fileobj)

    def restart(self) -> None:
        """
        Closes all client connections and restarts the server.
        """

        self.selector.close()
        self.selector = selectors.DefaultSelector()

        for client in self.CLIENTS.values():
            client.close()
        self.CLIENTS.clear()

        self.start()
        print("Server restarted")

    def accept_connection(self, listener_socket: socket.socket) -> None:
        """
        Accepts a new connection from a client.
        """

        conn, addr = listener_socket.accept()
        data = types.SimpleNamespace(addr=addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.selector.register(conn, events, data=data)

        # Get client name
        login = receive_data(conn, 64).decode(self.FORMAT).strip(' ')
        if login in self.CLIENTS:
            print(f"{login} is already connected to the server")
            send_data(conn, b'0', 1)
            conn.close()
            return
        send_data(conn, b'1', 1)
        self.CLIENTS[login] = conn
        print(f"{login} has connected to the server from {conn.getpeername()}")

    def close_client(self, sock: socket.socket) -> None:
        """
        Closes and unregisters a client socket.
        """

        self.selector.unregister(sock)
        sock.close()
        for login, client in list(self.CLIENTS.items()):
            if client == sock:
                print(f"{login} has disconnected from the server")
                del self.CLIENTS[login]

if __name__ == "__main__":
    server = Server()
    server.start()
