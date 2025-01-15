"""
FDP - File Delivery Protocol
"""

import server
import client


# FORMAT = The format (encryption) of the message to be received
DEFAULT_FORMAT = "utf-8"

# HEADERLEN = Information about the message to be received (in this case,
# the length of the message)
DEFAULT_HEADERDATALEN = 64

DEFAULT_PORT = 6969  # Default port number for the server


if __name__ == "__main__":
    local = None
    print("FDP - File Delivery Protocol")
    print("1. Host Server")
    print("2. Connect to Server")
    choice = int(input("Enter your choice: "))
    if choice == 1:
        local = server.Server()
        local.start()
    elif choice == 2:
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
        local = client.Client(login)
        local.connect()
    else:
        print("Invalid choice")
