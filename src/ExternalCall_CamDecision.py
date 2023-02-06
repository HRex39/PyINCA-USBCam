import time
import threading

import src.Global as GB

def runCameraDecision(thread_name):
    mutex = threading.Lock()
    while True:
        if GB.INCA_READY and not GB.VID_RECORD_START:
            mutex.acquire()
            GB.VID_DECISION = 1
            mutex.release()
        if GB.INCA_READY and GB.VID_RECORD_START and not GB.VID_RECORD_STOP:
            mutex.acquire()
            GB.VID_DECISION = 2
            mutex.release()
        if GB.VID_RECORD_STOP:
            mutex.acquire()
            GB.VID_DECISION = 3
            mutex.release()
        time.sleep(0.05) # 等等你的人民！！！