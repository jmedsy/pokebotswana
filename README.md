# PokeBotswana

An automation framework for mGBA. Instructions to and feedback from the emulator are handled through its [official scripting API](https://mgba.io/docs/scripting.html) (using Lua), while client automation and TCP socket communication are written in Python.

## Overview

From what I understand, similar functionality can be provided by using a mGBA build with Python Bindings, <small>which I failed to create with varying degrees of success (particularly for Windows)</small>...

Instead, we use a development build of mGBA which provides official Lua scripting!

Note: although nondevelopment builds <i>do</i> seem to have the UI option for Lua Scripting, it appears to be nonfunctional. <b>A Development build of mGBA is required for Lua Scriping</b>, which fortunately is available [on the mGBA website](https://mgba.io/downloads.html#development-downloads).

## Project Structure

```
pokebotswana/
├── mgba_scripting/
│   ├── client/          
|   |   ├── ...          
│   │   └── mgba_connection.py # Socket connection manager
│   └── server/                
│   │   └── socket_server.lua  # Manages mGBA I/O, actually run by mGBA
└── tools/
    └── save_manager/          # Save file management utilities (ignore, personal use)
```

## Quick Start

### 1. Setup mGBA

1. Download a [deveopment build of mGBA](https://mgba.io/downloads.html#development-downloads) (strongly recommended) or [compile your own](https://mgba.io/downloads.html#development-downloads) (may be necessary for features like headless-state).
2. Load your GBA ROM in mGBA
3. Enable Lua scripting in mGBA settings

### 2. Start the Lua Server

1. Copy `mgba_scripting/input/socket_server.lua` to your mGBA scripts directory
2. Load the script in mGBA
3. The server will start listening on port 8888 (or next available port)

### 3. Connect with Python

```python
from mgba_scripting.client.mgba_connection import MGBAConnection
from mgba_scripting.client.key_state import KeyManager

# Connect to mGBA
with MGBAConnection() as conn:
    # Create key manager
    key_mgr = KeyManager()
    
    # Press A button
    key_mgr.press_a()
    
    # Send key states to mGBA
    conn.send(key_mgr.serialize())
    
    # Listen for responses
    conn.listen()
```

## Key Components

### KeyManager

Manages button states and serializes them for transmission:

```python
from mgba_scripting.client.key_state import KeyManager

key_mgr = KeyManager()
key_mgr.press_a()
key_mgr.press_b()
key_mgr.release_a()

# Serialize to binary string (e.g., "1010000000")
binary_string = key_mgr.serialize()
```

### MGBAConnection

Handles socket communication with mGBA:

```python
from mgba_scripting.client.mgba_connection import MGBAConnection

with MGBAConnection(host="localhost", port=8888) as conn:
    conn.send("1010000000")  # Send key states
    conn.listen()  # Listen for responses
```

### KeyEvent

Represents individual key press/release events:

```python
from mgba_scripting.client.key_event import KeyEvent
from mgba_scripting.client.key_type import KeyType
from mgba_scripting.client.key_event_type import KeyEventType

# Create a press event
event = KeyEvent(KeyEventType.PRESS, KeyType.A)
```

## Communication Protocol

### Key State Format

Key states are transmitted as binary strings where each position represents a button:

```
Position: 0123456789
Buttons:  ABsS<>^vRL
Example:  1010000000  # A pressed, others not pressed
```

### Socket Communication

- **Protocol**: TCP
- **Default Port**: 8888
- **Data Format**: Binary strings (10 characters for 10 buttons)
- **Encoding**: UTF-8

## Development

### Running Tests

```bash
cd mgba_scripting/client
python test_socket.py
```

### Adding New Keys

1. Update `key_type.py` with new key definitions
2. Update the Lua server's `KEY_NAMES` table
3. Ensure both sides use the same key order

### Extending Functionality

The modular design makes it easy to add new features:

- **New Event Types**: Add to `key_event_type.py`
- **New Communication Protocols**: Extend `mgba_connection.py`
- **New Key Types**: Add to `key_type.py`

## Requirements

- Python 3.7+
- mGBA emulator
- Network connectivity (localhost)

## License

This project is for educational and automation purposes. Ensure you own the ROMs you're automating.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Troubleshooting

### Connection Issues
- Ensure mGBA is running with the Lua script loaded
- Check that port 8888 is not in use
- Verify firewall settings

### Key State Issues
- Ensure key order matches between Python and Lua
- Check that binary string length is exactly 10 characters
- Verify key state serialization format

### Performance Issues
- Consider using integer format instead of binary strings for better performance
- Implement connection pooling for high-frequency operations 