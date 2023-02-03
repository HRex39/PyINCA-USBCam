import threading
import win32com
import src.Global as GB
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

    def start_measurement(self):
        result = self.WorkExp.StartMeasurement()
        mutex = threading.Lock()
        if result:
            mutex.acquire()
            GB.INCA_READY = 1
            mutex.release()

        return result

    def stop_measurement(self):
        result = self.WorkExp.StartMeasurement()
        mutex = threading.Lock()
        if result:
            mutex.acquire()
            GB.INCA_READY = 0
            mutex.release()

        return result
