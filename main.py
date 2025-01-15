"""
FDP - File Delivery Protocol
"""

import server
import client

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
        local = client.Client(input("Enter your username: "))
        local.connect()
    else:
        print("Invalid choice")


