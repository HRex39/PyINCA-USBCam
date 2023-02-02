'''
Camera Threading
Author: HRex<hcr2077@outlook.com>
'''
import threading
import src.ExternalCall_INCA as EC_INCA
import src.ExternalCall_Cam as EC_Cam

if __name__ == '__main__':
    # Thread
    INCA_Thread = threading.Thread(target=EC_INCA.test, args=("INCA_Thread",))
    INCA_Thread.start()

    Camera_Thread = threading.Thread(target=EC_Cam.runCamera, args=("Camera_Thread",))
    Camera_Thread.setDaemon(True) # 守护线程，该子线程会随着主线程的退出而退出
    Camera_Thread.start()


    
    # point = [0,0,1]
    # pc = EC_Cam.convert_wc_to_cc(point)
    # print(pc)
    # pc = EC_Cam.convert_cc_to_pixel(pc)
    # print(pc)
