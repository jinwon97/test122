from flask import Flask, Response
from picamera2 import Picamera2
import cv2
import os
import time
import json
import psutil
import subprocess

app = Flask(__name__)

# 설정 파일 로드
with open("/home/jinwon97/raspi_stream/server/config/server_config.json", "r") as config_file:
    config = json.load(config_file)

resolution = tuple(config.get("resolution", [640, 480]))
format_ = config.get("format", "RGB888")
host = config.get("host", "0.0.0.0")
port = config.get("port", 5000)

# 자동으로 카메라 점유 프로세스 종료
def release_camera_resources():
    print("Releasing camera resources...")
    os.system("fuser -k /dev/media*")  # /dev/media* 점유 프로세스 종료

release_camera_resources()

# Picamera2 초기화
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": resolution, "format": format_}))
try:
    picam2.start()
except Exception as e:
    print(f"Error starting camera: {e}")
    exit(1)
#dfd
# 리소스 모니터링 함수
def monitor_resources():
    cpu_usage = psutil.cpu_percent(interval=0)
    memory = psutil.virtual_memory().percent
    gpu_mem = subprocess.check_output(["vcgencmd", "get_mem", "gpu"]).decode("utf-8").strip()
    return f"CPU: {cpu_usage:.2f}%, Memory: {memory:.2f}%, {gpu_mem}"

# FPS 및 레이턴시 출력
frame_count = 0
start_time = time.time()

def generate_frames():
    global frame_count, start_time
    while True:
        frame_start_time = time.time()
        frame = picam2.capture_array()

        # FPS 계산
        frame_count += 1
        elapsed_time = time.time() - start_time
        if elapsed_time > 1.0:
            print(f"FPS: {frame_count / elapsed_time:.2f}")
            frame_count = 0
            start_time = time.time()

        # 리소스 모니터링 출력
        print(monitor_resources())

        # JPEG 인코딩
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# MJPEG 스트림 엔드포인트
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# 리소스 상태 확인 엔드포인트
@app.route('/status')
def status():
    return monitor_resources()

if __name__ == "__main__":
    app.run(host=host, port=port, debug=False)
