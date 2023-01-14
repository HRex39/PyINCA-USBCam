import cv2
import time
import src.ExternalCall_INCA
import src.ExternalCall_Cam

if __name__ == '__main__':
    cap = cv2.VideoCapture(0) # Change device/mp4
    start_time = time.time()
    while True:
        ret, frame = cap.read()
        if (time.time() - start_time) != 0:  # 实时显示帧数
            fps = 1.0 / (time.time() - start_time)
            start_time = time.time()
        cv2.putText(frame, 'fps: ' + str(fps), (0, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.imshow("Video", frame)
        # 读取内容
        if cv2.waitKey(10) == ord("q"):
            break

    # 随时准备按q退出
    cap.release()
    cv2.destroyAllWindows()
    # 停止调用，关闭窗口