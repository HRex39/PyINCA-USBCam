import time
import multiprocessing


def runCameraDecision(thread_name, VID_DECISION, INCA_READY, VID_RECORD_START, VID_RECORD_STOP, INCA_EXIT):
    mutex = multiprocessing.Lock()
    while True:
        if INCA_READY.value and not VID_RECORD_START.value:
            mutex.acquire()
            VID_DECISION.value = 1
            mutex.release()
        if INCA_READY.value and VID_RECORD_START.value and not VID_RECORD_STOP.value:
            mutex.acquire()
            VID_DECISION.value = 2
            mutex.release()
        if VID_RECORD_STOP.value and not INCA_EXIT.value:
            mutex.acquire()
            VID_DECISION.value = 3
            mutex.release()
        if INCA_EXIT.value:
            break
        time.sleep(0.05) # 等等你的人民！！！