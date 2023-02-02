import threading, time
import src.Global as GB

def test(thread_name):
    mutex = threading.Lock()
    while True:
        time.sleep(2)
        mutex.acquire()
        GB.signal = not GB.signal
        print(GB.signal)
        mutex.release()