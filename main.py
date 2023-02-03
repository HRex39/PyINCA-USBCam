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

    Inca_App = Inca(work_address, exp_address, folder_address)
    threads = []
    # Thread
    INCA_Thread = threading.Thread(target=Inca_App.start_measurement, args=())
    Camera_Thread = threading.Thread(target=print_variable, args=())

    INCA_Thread.start()
    Camera_Thread.start()

    threads.append(INCA_Thread)
    threads.append(Camera_Thread)

    for i in range(len(threads)):
        threads[i].join()

    print("结束")

    
    # point = [0,0,1]
    # pc = EC_Cam.convert_wc_to_cc(point)
    # print(pc)
    # pc = EC_Cam.convert_cc_to_pixel(pc)
    # print(pc)
