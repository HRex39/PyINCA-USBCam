from math import sin, cos
import numpy as np
import cv2
import time
import multiprocessing

'''
1，世界坐标系
  世界坐标系可以任意选择，为假想坐标系，在被指定后随即 不变且唯一，即为绝对坐标系
2，相机坐标系
  相机坐标系以相机的光心（小孔）作为原点，X轴为水平方向，Y轴为竖直方向，Z轴指向相机所观察的方向，其随相机的移动而变化，即为相对坐标系
'''


camera_params = {
    # R，旋转矩阵
    "R": [[1, 0, 0],
          [0, 1, 0],
          [0, 0, 1]],
    # t，平移向量
    "T": [0, 0, 1],
    # camera_intrinsic, 相机内参
    # [[cx,0,u0],
    #  [0,cy,v0]]
    "camera_intrinsic": [[367.535, 0, 260.166],
                         [0, 367.535, 205.197], ]
}


def convert_wc_to_cc(point_world):
    """
        世界坐标系 -> 相机坐标系: R * pt + T:
        point_cam = np.dot(R, point_world.T) + T 
        :return: 3*1 matrix
        """
    point_world = np.asarray(point_world)
    R = np.asarray(camera_params["R"])
    T = np.asarray(camera_params["T"])
    # .T is 转置, T is translation mat
    point_cam = np.dot(R, point_world.T) + T  # R * (pt - T)
    return point_cam


def convert_cc_to_pixel(point_cam):
    """
    相机坐标系 -> 像素坐标系: R * pt + T:
    point_pixel = np.dot(camera_intrinsic, point_cam)
    :return: 2*1
    """
    camera_intrinsic = camera_params["camera_intrinsic"]
    point_pixel = np.dot(camera_intrinsic, point_cam)
    return point_pixel


def rpy2quaternion(roll, pitch, yaw):
    x = sin(pitch / 2) * sin(yaw / 2) * cos(roll / 2) + cos(pitch / 2) * cos(yaw / 2) * sin(roll / 2)
    y = sin(pitch / 2) * cos(yaw / 2) * cos(roll / 2) + cos(pitch / 2) * sin(yaw / 2) * sin(roll / 2)
    z = cos(pitch / 2) * sin(yaw / 2) * cos(roll / 2) - sin(pitch / 2) * cos(yaw / 2) * sin(roll / 2)
    w = cos(pitch / 2) * cos(yaw / 2) * cos(roll / 2) - sin(pitch / 2) * sin(yaw / 2) * sin(roll / 2)
    q = [x, y, z, w]
    return q


def quaternion_to_rotation_matrix(q):  # x, y ,z ,w
    rot_matrix = np.array(
        [[1.0 - 2 * (q[1] * q[1] + q[2] * q[2]), 2 * (q[0] * q[1] - q[3] * q[2]), 2 * (q[3] * q[1] + q[0] * q[2])],
         [2 * (q[0] * q[1] + q[3] * q[2]), 1.0 - 2 * (q[0] * q[0] + q[2] * q[2]), 2 * (q[1] * q[2] - q[3] * q[0])],
         [2 * (q[0] * q[2] - q[3] * q[1]), 2 * (q[1] * q[2] + q[3] * q[0]), 1.0 - 2 * (q[0] * q[0] + q[1] * q[1])]],
        dtype=q.dtype)
    return rot_matrix

class Camera(object):

    def __init__(self, threading_name, device_id):
        self.threading_name = threading_name
        self.device_id = device_id

    def runCamera(self, VID_DECISION, VID_READY, VID_START_RECORD_TIME, VID_RECORD_READY, INCA_RECORD_STOP, INCA_EXIT):
        mutex = multiprocessing.Lock()
        flag_break = 0
        flag_cap = [0, 0, 0, 0]
        cap = cv2.VideoCapture(self.device_id) # Will just cap one Cam
        while True and not flag_break:
            start_time = time.time()
            if VID_DECISION.value == 1:
                if flag_cap[1] == 0:
                    cv2.destroyAllWindows()
                    cap = cv2.VideoCapture(self.device_id)
                    flag_cap = [0, 1, 0, 0]
                ret, frame = cap.read()
                if (time.time() - start_time) != 0:  # 实时显示帧数
                    fps = 1.0 / (time.time() - start_time)
                    start_time = time.time()

                cv2.putText(frame, 'show: ' + str(fps), (0, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                cv2.imshow("Video - GB.VID_DECISION=1", frame)
                mutex.acquire()
                VID_READY.value = 1
                mutex.release()

                if cv2.waitKey(10) == ord("q"):# 随时准备按q退出
                    flag_break = 1
                    flag_cap = [0,0,0,0]
                    cap.release()
                    cv2.destroyAllWindows()# 停止调用，关闭窗口
                    break

            if VID_DECISION.value == 2:
                if flag_cap[2] == 0:
                    cv2.destroyAllWindows()
                    cap = cv2.VideoCapture(self.device_id)
                    VID_START_RECORD_TIME.value = time.time()
                    mutex.acquire()
                    VID_RECORD_READY.value = 1
                    mutex.release()
                    flag_cap = [0,0,1,0]
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
                filename = "video_result_" + str(time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime(time.time()))) + ".mp4"
                writer = cv2.VideoWriter(filename, fourcc, fps, (width, height))

                while cap.isOpened():
                    ret, frame = cap.read()  # 读取摄像头画面
                     # print("\r"+"Saving Video...", end="")
                    if ret == True:
                        writer.write(frame)  # 视频保存
                    if INCA_RECORD_STOP.value == 1:
                        break

                cap.release()
                writer.release()
                time.sleep(1)
                mutex.acquire()
                VID_RECORD_READY.value = 0
                mutex.release()
                cv2.destroyAllWindows()# 停止调用，关闭窗口
            
            if VID_DECISION.value == 3:
                if flag_cap[3] == 0:
                    cv2.destroyAllWindows()
                    flag_cap = [0,0,0,1]
                time.sleep(0.1)

            if INCA_EXIT.value:
                break

