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

def send_file(socket, file_path, HEADERDATALEN, FORMAT, FILE_CHUNK_SIZE):
    # Could use socket.sendfile() but where's the fun in that?
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

def receive_file(socket, HEADERDATALEN, FORMAT, FILE_CHUNK_SIZE, file_path):
    if os.path.exists(file_path):
        file_name, file_extension = os.path.splitext(file_path)
        n = 1
        while os.path.exists(f"{file_name} ({n}){file_extension}"):
            n += 1
        file_path = f"{file_name} ({n}){file_extension}"

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