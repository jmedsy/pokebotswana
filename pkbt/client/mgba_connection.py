import socket
import time
import threading
import msvcrt
from typing import Optional, Callable
from pkbt.input.key_event import KeyEvent
from pkbt.input.key_event_type import KeyEventType
from pkbt.input.key_type import KeyType, KEY_TYPES
from pkbt.input.key_state import KeyState

"""Control characters for other non-key state messages"""
RESET_CTRL_CHAR = "\x02"
SCREENSHOT_CTRL_CHAR = "\x03"

class MGBAConnection:
    _host: str
    _port: int
    _socket: Optional[socket.socket] = None
    _connected: bool
    _on_message: Optional[Callable] = None
    _ping_thread: Optional[threading.Thread] = None
    _stop_ping: bool = False

    def __init__(self, host="localhost", port=8888):
        self._host = host
        self._port = port
        self._socket = None
        self._connected = False
        self._on_message = None
        self._key_state = KeyState()
        self._ping_thread = None
        self._stop_ping = False

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
        self._stop_ping = True
        if self._ping_thread and self._ping_thread.is_alive():
            self._ping_thread.join(timeout=1.0)
        
        if self._socket:
            self._socket.close()
            self._socket = None
        self._connected = False
        print("Disconnected from MGBA")

    def ping(self):
        """Send a ping to keep the connection alive"""
        if self._connected and self._socket:
            try:
                self._socket.send("ping\n".encode())
            except Exception as e:
                print(f"Ping failed: {e}")
                self._connected = False

    def _ping_loop(self):
        """Background thread to send periodic pings"""
        while self._connected and not self._stop_ping:
            time.sleep(2.0)  # Ping every 2 seconds
            if not self._stop_ping:
                self.ping()

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
        """Listen for messages from mGBA with ping and escape key handling"""
        if not self._connected or not self._socket:
            print("Not connected to mGBA")
            return

        self._on_message = callback
        
        # Start ping thread
        self._ping_thread = threading.Thread(target=self._ping_loop, daemon=True)
        self._ping_thread.start()

        print("Connected! Press ESC to disconnect.")
        
        try:
            while self._connected:
                # Check for escape key
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if key == b'\x1b':  # ESC key
                        print("ESC pressed - disconnecting...")
                        break
                
                # Try to receive data with a short timeout
                try:
                    self._socket.settimeout(0.1)  # 100ms timeout
                    data = self._socket.recv(1024).decode()
                    if data:
                        if self._on_message:
                            self._on_message(data.strip())
                        else:
                            print(f"Received: {data.strip()}")
                except socket.timeout:
                    # Timeout is expected, continue
                    pass
                except Exception as e:
                    print(f"Listen failed: {e}")
                    self._connected = False
                    break
        finally:
            self.disconnect()

    def execute_event(self, key_event: KeyEvent):
        """Execute a key event"""
        match key_event.event_type:
            case KeyEventType.PUSH:
                self._key_state.set_key(key_event.key_type, True)
                self.send(self._key_state.serialize_bitmask())
                time.sleep(key_event.push_time)
                self._key_state.set_key(key_event.key_type, False)
                self.send(self._key_state.serialize_bitmask())
            case KeyEventType.HOLD:
                self._key_state.set_key(key_event.key_type, True)
                self.send(self._key_state.serialize_bitmask())
            case KeyEventType.RELEASE:
                self._key_state.set_key(key_event.key_type, False)
                self.send(self._key_state.serialize_bitmask())

    def reset_game(self):
        """Reset the game"""
        self.send(RESET_CTRL_CHAR + "\n")

    def save_screenshot_to_file(self, filename: str):
        """Take a screenshot and save it to a file"""
        self.send(SCREENSHOT_CTRL_CHAR + filename + "\n")

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

        for key in KEY_TYPES:
            print(f"Pressing {key}")
            conn.execute_event(KeyEvent(KeyEventType.HOLD, key))
            time.sleep(1)
            conn.execute_event(KeyEvent(KeyEventType.RELEASE, key))
            time.sleep(1)
        
        conn.save_screenshot_to_file("fooshot.png")
        conn.reset_game()
        conn.listen(callback=handle_keystate)