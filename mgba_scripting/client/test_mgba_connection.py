from mgba_connection import MGBAConnection

def handle_keystate(data):
    print(f"Key state: {data}")

with MGBAConnection('localhost', 8888) as conn:
    conn.send("Start")
    conn.listen(callback=handle_keystate)