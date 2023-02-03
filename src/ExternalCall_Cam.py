from math import sin, cos
import numpy as np
import cv2
import time

import src.Global as GB

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

def runCamera(thread_name):
    while True:
        cap = cv2.VideoCapture(0) # Change device/mp4
        start_time = time.time()
        while GB.INCA_READY:
            print(thread_name, GB.INCA_READY)
            ret, frame = cap.read()
            if (time.time() - start_time) != 0:  # 实时显示帧数
                fps = 1.0 / (time.time() - start_time)
                start_time = time.time()
            cv2.putText(frame, 'fps: ' + str(fps), (0, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            cv2.imshow("Video", frame)
            if cv2.waitKey(10) == ord("q"):
                break
        # 随时准备按q退出
        cap.release()
        cv2.destroyAllWindows()
        # 停止调用，关闭窗口