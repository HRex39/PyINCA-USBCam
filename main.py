'''
Camera Threading
Author: HRex<hcr2077@outlook.com>
'''
import threading
from src.ExternalCall_INCA import Inca
import src.ExternalCall_Cam as EC_Cam
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

    # !!! init hardware
    # Inca_App.init_hardware()

    # Inca_App.set_record()
    threads = []
    # Thread
    # INCA_Thread = threading.Thread(target=Inca_App.start_measurement, args=())

    Inca_App.start_measurement()
    Camera_Thread = threading.Thread(target=EC_Cam.runCamera, args=("Camera_Thread",))
    Camera_Thread.start()

    threads.append(Camera_Thread)

    threads.clear()

    if GB.INCA_READY and GB.VID_READY:
        print('yes\n')

    for i in range(len(threads)):
        threads[i].join()

    print("结束")

    
    # point = [0,0,1]
    # pc = EC_Cam.convert_wc_to_cc(point)
    # print(pc)
    # pc = EC_Cam.convert_cc_to_pixel(pc)
    # print(pc)
