import os
from enum import IntEnum

from tqdm import tqdm


class DataType(IntEnum):
    DEBUG = 0
    COMMAND = 1
    UPLOAD_FILE = 2
    DOWNLOAD_FILE = 3
    FILES_INFO = 4
    DELETE_FILE = 5
    DISCONNECT = 6

def receive_data(socket, data_len):
    data = b""
    while len(data) < data_len:
        packet = socket.recv(data_len - len(data))
        if not packet:
            return None
        data += packet
    return data

def send_data(socket, data, data_len):
    if len(data) < data_len:
        data += b' ' * (data_len - len(data))
    elif len(data) > data_len:
        data = data[:data_len]

    data_sent = 0
    while data_sent < data_len:
        data_sent += socket.send(data[data_sent:])

def send_file(socket, file_path, HEADERDATALEN, FORMAT, FILE_CHUNK_SIZE, send_file_name=True):
    # Could use socket.sendfile() but where's the fun in that?
    if send_file_name:
        file_name = os.path.basename(file_path).encode(FORMAT)
        file_name_size = str(len(file_name)).encode(FORMAT)

        send_data(socket, file_name_size, HEADERDATALEN)
        send_data(socket, file_name, len(file_name))

    print("[FILE] Started sending file: ", os.path.basename(file_path))

    file_size = os.path.getsize(file_path)
    send_data(socket, str(file_size).encode(FORMAT), HEADERDATALEN)

    chunks = file_size // FILE_CHUNK_SIZE
    remaining_data = file_size % FILE_CHUNK_SIZE
    # print("[DEBUG] File size: ", file_size)
    # print("[DEBUG] Number of chunks: ", chunks)
    # print("[DEBUG] Remaining data: ", remaining_data)

    with open(file_path, "rb") as file:
        for chunk in tqdm(range(chunks + 1), desc="Sending file", unit="chunk"):
            size = FILE_CHUNK_SIZE if chunk < chunks else remaining_data
            file_data = file.read(size)
            if not file_data:
                break
            send_data(socket, file_data, size)

def receive_file(socket, HEADERDATALEN, FORMAT, FILE_CHUNK_SIZE, file_save_dir=None, file_path=None):
    if file_save_dir is not None and file_path is None:
        file_name_size = int(receive_data(socket, HEADERDATALEN).decode(FORMAT))
        file_name = receive_data(socket, file_name_size).decode(FORMAT)

        if not os.path.exists(file_save_dir):
            os.makedirs(file_save_dir)
        file_path = os.path.join(file_save_dir, file_name)

    # TODO: Check if file already exists, if so, rename it to f"{file_name} ({n})"
    print("[DEBUG] Receiving file: ", os.path.basename(file_path))

    file_size = int(receive_data(socket, HEADERDATALEN).decode(FORMAT))

    chunks = file_size // FILE_CHUNK_SIZE
    remaining_data = file_size % FILE_CHUNK_SIZE
    with open(file_path, "wb") as file:
        for chunk in tqdm(range(chunks + 1), desc=f"Receiving file", unit="chunk"):
            size = FILE_CHUNK_SIZE if chunk < chunks else remaining_data
            data = receive_data(socket, size)
            if not data:
                break
            file.write(data)