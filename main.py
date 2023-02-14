'''
Camera Threading
Author: HRex<hcr2077@outlook.com>
'''
import threading
import time

from src.ExternalCall_INCA import Inca
import src.ExternalCall_Cam as Cam
import src.ExternalCall_CamDecision as CamDecision
import src.Global as GB
import argparse


def print_variable():
    while True:
        print(0)
        if GB.INCA_READY == 1:
            print("GB.INCA_READY is ", GB.INCA_READY)
            return


if __name__ == '__main__':

    '''
    parse = argparse.ArgumentParser()
    parse.add_argument('-e', type=str, required=True)
    parse.add_argument('-w', type=str, required=True)
    parse.add_argument('-f', type=str, required=True)

    args = parse.parse_args()
    '''
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

    Inca_App.start_measurement()
    # Cam Decision Thread
    Camera_Decision_Thread = threading.Thread(target=CamDecision.runCameraDecision, args=("Camera_Decision_Thread",))
    Camera_Decision_Thread.setDaemon(True) # 守护线程，该子线程会随着主线程的退出而退出
    Camera_Decision_Thread.start()
    # Cam Run Thread
    Cam1 = Cam.Camera("Cam1_Thread")
    Camera_Thread = threading.Thread(target=Cam1.runCamera)
    Camera_Thread.setDaemon(True) # 守护线程，该子线程会随着主线程的退出而退出
    Camera_Thread.start()

    while True:
        if GB.INCA_READY and GB.VID_READY:
            decision = int(input("是否开始记录: "))
            print("\n")
            # 0 不记录并停止测量 1 开始记录
            if decision == 0:
                Inca_App.stop_measurement()
                print("stop measurement!\n")
                break
            elif decision == 1:
                GB.count_number += 1
                GB.VID_RECORD_START = 1
                while not GB.VID_RECORD_READY:
                    pass
                Inca_App.start_record()
                GB.START_RECORD_TIME = time.time()
                print("start recording\n")
            else:
                print("wrong input, exit\n")
                break

            decision_1 = int(input("是否停止记录: "))
            print("\n")

            # 0 中止并丢弃数据 1 中止并保存数据
            if decision_1 == 0:
                Inca_App.stop_record_with_discard()
            elif decision_1 == 1:
                Inca_App.stop_record()
            else:
                print("wrong input, exit")
                break

            GB.VID_STOP_RECORD_TIME = time.time()

            log_file_name = "log_" + str(GB.count_number) + ".txt"
            with open(log_file_name, 'a') as f:
                f.write("Inca_file_time: ")
                f.write(str(GB.VID_STOP_RECORD_TIME))
                f.write('\n')
                offset_time = GB.VID_START_RECORD_TIME - GB.START_RECORD_TIME
                f.write("offset time is: ")
                f.write(str(offset_time))
                f.write('\n')

            GB.VID_RECORD_START = 0

            decision_2 = int(input("是否重新开始测量: "))
            print("\n")

            # 0 直接退出 1 重新开始测量

            if decision_2 == 0:
                Inca_App.close_inca()
                print('inca yes\n')
                break
            elif decision_1 == 1:
                Inca_App.start_measurement()
            else:
                print("wrong input, exit\n")
                break
        else:
            print("conditions not correct!\n")
            time.sleep(0.1)

    print("结束")

    
    # point = [0,0,1]
    # pc = EC_Cam.convert_wc_to_cc(point)
    # print(pc)
    # pc = EC_Cam.convert_cc_to_pixel(pc)
    # print(pc)
