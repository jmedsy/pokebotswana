import socket
import time
from typing import Optional, Callable
from key_event import KeyEvent
from key_event_type import KeyEventType
from key_type import KeyType
from key_state import KeyState

class MGBAConnection:
    _host: str
    _port: int
    _socket: Optional[socket.socket] = None
    _connected: bool
    _on_message: Optional[Callable] = None

    def __init__(self, host="localhost", port=8888):
        self._host = host
        self._port = port
        self._socket = None
        self._connected = False
        self._on_message = None
        self._key_state = KeyState()

    def connect(self) -> bool:
        """Connect to the MGBA server (see socket_server.lua)"""
        try:
            self._socket = socket.socket()
            self._socket.settimeout(5.0)
            self._socket.connect((self._host, self._port))
            self._connected = True
            print (f"Connected to mGBA on {self._host}:{self._port}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def disconnect(self):
        """Disconnect from mGBA"""
        if self._socket:
            self._socket.close()
            self._socket = None
        self._connected = False
        print("Disconnected from MGBA")

    def send(self, message: str) -> bool:
        """Send a message to mGBA"""
        if not self._connected or not self._socket:
            print("Not connected to mGBA")
            return False

        try:
            self._socket.send(message.encode())
            return True
        except Exception as e:
            print(f"Send failed: {e}")
            self._connected = False
            return False

    def listen(self, callback: Optional[Callable]):
        """Listen for messages from mGBA"""
        if not self._connected or not self._socket:
            print("Not connected to mGBA")
            return

        self._on_message = callback

        try:
            while self._connected:
                data = self._socket.recv(1024).decode()
                if data:
                    if self._on_message:
                        self._on_message(data.strip())
                    else:
                        print(f"Received: {data.strip()}")
        except Exception as e:
            print(f"Listen failed: {e}")
            self._connected = False
        finally:
            self.disconnect()

    def execute_event(self, key_event: KeyEvent):
        """Execute a key event"""
        match key_event.event_type:
            case KeyEventType.PUSH:
                self._key_state.set_key(key_event.key_type, True)
                self.send(self._key_state.serialize())
                time.sleep(key_event.push_time)
                self._key_state.set_key(key_event.key_type, False)
                self.send(self._key_state.serialize())
            case KeyEventType.HOLD:
                self._key_state.set_key(key_event.key_type, True)
                self.send(self._key_state.serialize())
            case KeyEventType.RELEASE:
                self._key_state.set_key(key_event.key_type, False)
                self.send(self._key_state.serialize())

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

if __name__ == "__main__":
    def handle_keystate(data):
        print(f"Key state: {data}")

    with MGBAConnection('localhost', 8888) as conn:
        conn.execute_event(KeyEvent(KeyEventType.PUSH, KeyType.A))
        # conn.send("Start")
        conn.listen(callback=handle_keystate)