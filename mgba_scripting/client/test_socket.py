import socket
import time

# # Connect to mGBA
# client = socket.socket()
# client.connect(("localhost", 8888))
# print("Connected to mGBA!")

# # Send a test message
# client.send(b"S")
# print("Sent: hello")

# # Keep connection alive to see responses
# time.sleep(5)
# client.close()

def listen_for_keystates():
    client = socket.socket()
    client.connect(("localhost", 8888))

    # Listen for key state updates from mGBA
    while True:
        try:
            data = client.recv(1024).decode()
            if data:
                print(f"Key state: {data.strip()}")
        except:
            break

    client.close()

listen_for_keystates()