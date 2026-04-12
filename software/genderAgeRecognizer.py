import cv2
import threading
import time
from deepface import DeepFace


# --- 1. 定义一个独立的摄像头读取线程 ---
class CameraStream:
    def __init__(self, url):
        self.cap = cv2.VideoCapture(url)
        self.ret, self.frame = self.cap.read()
        self.running = True
        # 启动后台线程
        threading.Thread(target=self.update, daemon=True).start()

    def update(self):
        # 这个线程的任务就是疯狂清空缓冲区，保证 self.frame 永远是最新的一帧
        while self.running:
            self.ret, self.frame = self.cap.read()

    def read(self):
        return self.ret, self.frame

    def stop(self):
        self.running = False
        self.cap.release()


# --- 2. 主程序 ---
url = "http://192.168.43.244:81/stream"
cam = CameraStream(url)
time.sleep(2)  # 等待摄像头预热

# 缓存识别结果，避免画面闪烁
current_gender = "Unknown"
current_age = 0
box = (0, 0, 0, 0)
last_analyze_time = 0

while True:
    ret, frame = cam.read()
    if not ret or frame is None:
        continue

    # 复制一帧用来画图，避免多线程读写冲突
    display_frame = frame.copy()
    current_time = time.time()

    # --- 3. 限制 AI 大脑的思考频率（例如每 1 秒只思考一次）---
    # 这样可以保证画面流畅（30FPS），只是年龄/性别标签每秒更新一次
    if current_time - last_analyze_time > 1.0:
        try:
            # 优化：增加 detector_backend='opencv'，使用最快（但略微牺牲精度）的检测器
            results = DeepFace.analyze(
                frame,
                actions=['age', 'gender'],
                enforce_detection=False,
                detector_backend='opencv'  # 核心加速参数！
            )

            # 获取最新结果
            res = results[0]  # 如果有多个人脸，这里简单取第一个
            x, y, w, h = res['region']['x'], res['region']['y'], res['region']['w'], res['region']['h']
            box = (x, y, w, h)
            current_gender = res['dominant_gender']
            current_age = res['age']
            if current_age < 40:
                current_age -= 10

            if current_gender == 'Man':
                if current_age < 18:
                    print("原来是弟弟啊lol")
                else:
                    print("大叔")
            elif current_gender == 'Woman':
                if current_age < 18:
                    print("妹妹")
                else:
                    print("阿姨")

        except Exception as e:
            pass  # 未检测到人脸时静默

        last_analyze_time = current_time

    # --- 4. 无论 AI 算没算完，画面都在流畅渲染 ---
    if box != (0, 0, 0, 0):
        x, y, w, h = box
        cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(display_frame, f"{current_gender}, {current_age}", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow('ESP32-S3 AI Brain', display_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.stop()
cv2.destroyAllWindows()
