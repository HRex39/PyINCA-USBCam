import multiprocessing
import time
import ctypes
import sys

from src.ExternalCall_INCA import Inca
import src.ExternalCall_Cam as Cam
import src.ExternalCall_CamDecision as CamDecision
import argparse

if __name__ == '__main__':

    '''
    parse = argparse.ArgumentParser()
    parse.add_argument('-e', type=str, required=True)
    parse.add_argument('-w', type=str, required=True)
    parse.add_argument('-f', type=str, required=True)

    args = parse.parse_args()
    '''

    # --- Inca Modify --- #
    # use this signal to show the inca status
    INCA_READY = multiprocessing.Manager().Value(ctypes.c_int, 0)
    # use this signal to start video recording
    VID_RECORD_START = multiprocessing.Manager().Value(ctypes.c_int, 0)
    # use this signal to discard both inca and video file
    VID_DO_NOT_SAVE = multiprocessing.Manager().Value(ctypes.c_int, 0)
    # use this to stop the inca record and save
    INCA_RECORD_STOP = multiprocessing.Manager().Value(ctypes.c_int, 0)
    # use this to stop the video record and save
    VID_RECORD_STOP = multiprocessing.Manager().Value(ctypes.c_int, 0)

    # --- Cam Modify --- #
    # Cam Decision
    VID_DECISION = multiprocessing.Manager().Value(ctypes.c_int, 0)
    # Cam Ready Status
    VID_READY = multiprocessing.Manager().Value(ctypes.c_int, 0)
    # Cam Record Status
    VID_RECORD_READY = multiprocessing.Manager().Value(ctypes.c_int, 0)
    # ---time point--- #

    START_RECORD_TIME = multiprocessing.Manager().Value(ctypes.c_float, 0)
    STOP_RECORD_TIME = multiprocessing.Manager().Value(ctypes.c_float, 0)
    VID_START_RECORD_TIME = multiprocessing.Manager().Value(ctypes.c_float, 0)
    VID_STOP_RECORD_TIME = multiprocessing.Manager().Value(ctypes.c_float, 0)

    # --- file count --- #

    count_number = multiprocessing.Manager().Value(ctypes.c_int, 0)

    # --- exit method --- #

    INCA_EXIT = multiprocessing.Manager().Value(ctypes.c_int, 0)

    exp_address = '166_13834_MY24_ACP2_1_auto_backup_1'
    work_address = 'Workspace'
    folder_address = '16733'
    pathname = 'C:\\Users\\Public\\Documents\\ETAS\\INCA7.3\\Measure\\'
    filename = 'DU24IV024_RVB'
    increament_flag = 1

    Inca_App = Inca(work_address, exp_address, folder_address)
    Inca_App.set_record(pathname, filename, increament_flag)

    # !!! init hardware 0 do not init 1 init
    init_or_not = int(input("是否需要初始化硬件： "))
    print("\n")
    if init_or_not == 1:
        Inca_App.init_hardware()

    # Inca_App.set_record()

    # Thread
    # INCA_Thread = threading.Thread(target=Inca_App.start_measurement, args=())

    Inca_App.start_measurement(INCA_READY)
    p2 = multiprocessing.Process(target=CamDecision.runCameraDecision, args=(
    "Camera_Decision_Thread", VID_DECISION, INCA_READY, VID_RECORD_START, VID_RECORD_STOP, INCA_EXIT))
    Cam1 = Cam.Camera(threading_name="Cam1_Thread", device_id=0)
    p3 = multiprocessing.Process(target=Cam1.runCamera, args=(
    count_number, VID_DECISION, VID_READY, VID_START_RECORD_TIME, VID_RECORD_READY, INCA_RECORD_STOP, INCA_EXIT))

    p2.start()
    p3.start()

    while True:
        if INCA_READY.value and VID_READY.value:
            decision = int(input("是否开始记录: "))
            print("\n")
            # 0 不记录并停止测量 1 开始记录
            if decision == 0:
                Inca_App.stop_measurement(INCA_READY)
                print("stop measurement!\n")
                break
            elif decision == 1:
                count_number.value = count_number.value + 1
                VID_RECORD_START.value = 1
                while not VID_RECORD_READY.value:
                    pass
                Inca_App.start_record(VID_RECORD_STOP)
                START_RECORD_TIME.value = time.time()
                print("start recording\n")
            else:
                print("wrong input, exit\n")
                break

            decision_1 = int(input("是否停止记录: "))
            print("\n")

            # 0 中止并丢弃数据 1 中止并保存数据
            if decision_1 == 0:
                Inca_App.stop_record_with_discard(VID_DO_NOT_SAVE, INCA_RECORD_STOP, VID_RECORD_START, VID_RECORD_STOP)
            elif decision_1 == 1:
                Inca_App.stop_record(VID_DO_NOT_SAVE, INCA_RECORD_STOP, VID_RECORD_START, VID_RECORD_STOP)
            else:
                print("wrong input, exit")
                break

            VID_STOP_RECORD_TIME.value = time.time()

            log_file_name = "log_" + str(count_number.value) + ".txt"
            with open(log_file_name, 'a') as f:
                f.write("Inca_file_time: ")
                f.write(str(VID_STOP_RECORD_TIME))
                f.write('\n')
                offset_time = VID_START_RECORD_TIME.value - START_RECORD_TIME.value
                f.write("offset time is: ")
                f.write(str(offset_time))
                f.write('\n')

            decision_2 = int(input("是否重新开始测量: "))
            print("\n")

            # 0 直接退出 1 重新开始测量

            if decision_2 == 0:
                Inca_App.close_inca(INCA_EXIT)
                print('inca yes\n')
                break
            elif decision_2 == 1:
                VID_RECORD_START.value = 0
                INCA_READY.value = 0
                VID_DO_NOT_SAVE.value = 0
                INCA_RECORD_STOP.value = 0
                VID_RECORD_STOP.value = 0
                VID_READY.value = 0
                VID_RECORD_READY.value = 0
                Inca_App.start_measurement(INCA_READY)
            else:
                print("wrong input, exit\n")
                break
        else:
            # print("conditions not correct!\n")
            time.sleep(0.1)

    p2.join()
    p3.join()

    print("all process dead\n")
    
    # point = [0,0,1]
    # pc = EC_Cam.convert_wc_to_cc(point)
    # print(pc)
    # pc = EC_Cam.convert_cc_to_pixel(pc)
    # print(pc)
