import cv2
from deepface import DeepFace

# 1. 替换为你的 ESP32-S3 流地址
url = "http://192.168.43.244:81/stream"
cap = cv2.VideoCapture(url)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 2. 每隔几帧分析一次，避免电脑卡顿
    try:
        # DeepFace 核心分析代码：同时分析年龄、性别
        results = DeepFace.analyze(frame, actions=['age', 'gender'], enforce_detection=False)

        for res in results:
            x, y, w, h = res['region']['x'], res['region']['y'], res['region']['w'], res['region']['h']
            gender = res['dominant_gender']
            age = res['age']

            # 3. 在画面上画框并标注
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"{gender}, {age}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # 4. 根据结果给 ESP32 发指令（这里可以扩展 HTTP 请求）
            if gender == 'Man' and age > 18:
                print("检测到成年男性，发送指令：OPEN")
    except Exception as e:
        print("未检测到人脸")

    cv2.imshow('ESP32-S3 AI Brain', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
