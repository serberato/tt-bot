import threading
import time

def run():
    print("Starting background event loop")
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("This won't be caught in a background thread on Windows.")

t = threading.Thread(target=run, daemon=True)
t.start()

print("Main thread waiting. Press Ctrl+C...")
try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    print("Caught Ctrl+C in main thread!")
