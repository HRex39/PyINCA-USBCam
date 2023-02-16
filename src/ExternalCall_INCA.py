import multiprocessing
import win32com
from win32com.client import Dispatch, constants


class Inca(object):

    def __init__(self, workspace_address, exp_address, folder_address):
        self.w = win32com.client.Dispatch('inca.inca')
        self.DB = self.w.GetCurrentDataBase()
        WS = self.DB.BrowseItemInFolder(workspace_address, folder_address)
        # get Hardware
        self.HwApp = WS[0]
        # get exp
        Exp = self.DB.BrowseItemInFolder(exp_address, folder_address)
        ExpApp = Exp[0]
        ExpView = ExpApp.OpenExperiment()
        self.WorkExp = ExpView.GetExperiment()

    def init_hardware(self):
        return self.WorkExp.InitializeHardware()

    def set_record(self, pathname, filename, increament_flag=1):
        self.WorkExp.SetRecordingPathName(pathname)
        self.WorkExp.SetRecordingFileName(filename)
        self.WorkExp.SetRecordingFileAutoincrementFlag(increament_flag)

    def get_measure_value(self, ValueName):
        return self.WorkExp.GetMeasureElement(ValueName)

    def start_measurement(self, INCA_READY):
        result = self.WorkExp.StartMeasurement()
        mutex = multiprocessing.Lock()
        if result:
            mutex.acquire()
            INCA_READY.value = 1
            mutex.release()

        return result

    def start_record(self, VID_RECORD_STOP):
        result = self.WorkExp.StartRecording()
        mutex = multiprocessing.Lock()
        if result:
            mutex.acquire()
            # GB.VID_RECORD_START = 1
            VID_RECORD_STOP.value = 0
            mutex.release()
        return result

    def stop_record_with_discard(self, VID_DO_NOT_SAVE, INCA_RECORD_STOP, VID_RECORD_START, VID_RECORD_STOP):
        result = self.WorkExp.StopAndDiscardRecording()
        mutex = multiprocessing.Lock()
        if result:
            mutex.acquire()
            VID_DO_NOT_SAVE.value = 1
            INCA_RECORD_STOP.value = 1
            VID_RECORD_START.value = 0
            VID_RECORD_STOP.value = 1
            mutex.release()
        return result

    def stop_record(self, VID_DO_NOT_SAVE, INCA_RECORD_STOP, VID_RECORD_START, VID_RECORD_STOP):
        result = self.WorkExp.StopRecording(self.WorkExp.GetRecordingFileName(), self.WorkExp.GetRecordingFileFormat())
        mutex = multiprocessing.Lock()
        if result:
            mutex.acquire()
            VID_DO_NOT_SAVE.value = 0
            INCA_RECORD_STOP.value = 1
            VID_RECORD_START.value = 0
            VID_RECORD_STOP.value = 1
            mutex.release()
        return result

    def stop_measurement(self, INCA_READY):
        result = self.WorkExp.StopMeasurement()
        mutex = multiprocessing.Lock()
        if result:
            mutex.acquire()
            INCA_READY.value = 0
            mutex.release()

        return result

    def close_inca(self, INCA_EXIT):
        result = self.w.CloseTool()
        mutex = multiprocessing.Lock()
        if result:
            mutex.acquire()
            INCA_EXIT.value = 1
            mutex.release()

        return result
