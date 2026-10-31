# Smart Automated Parking & Gate Management System

An edge-AI automated parking management infrastructure built for final-year evaluation. The system captures live video traffic from an edge node, streams frames across a local wireless network, extracts vehicle alphanumeric indexing metrics via deep-learning computer vision models, updates a web transaction logging panel, and drives physical mechanical gate isolation relays.

---

## 🛠️ 1. Hardware Architecture

*   **Computing Node:** Raspberry Pi 4 Model B (Broadcom BCM2711, Quad-core Cortex-A72 @ 1.5GHz).
*   **Operating System:** Raspberry Pi OS Lite (64-bit Debian Bookworm, Kernel 6.12+).
*   **Video Capture Subsystem:** Raspberry Pi Camera Module Rev 1.3 (OmniVision OV5647 5MP Sensor).
*   **Display Interface:** 3.5-inch RPi Touch Screen Shield (SKU: MPI3501, ILI9486 LCD Controller, XPT2046 Touch Matrix via SPI data bus).
*   **Actuator Control:** 5V Low-Voltage Single-Channel Isolated Relay Board (Linked to BCM GPIO 18 / Physical Pin 12).
*   **Central processing Server:** Cross-platform Laptop (Ubuntu Linux / Windows 11 Node) running on a local wireless router network (`Rohan WIFI`).

---

## ⚙️ 2. Software Stack & Dependencies

The server engine runs on Python 3.10+. Dependencies are managed via a centralized requirements architecture.

### Project Directory Structure
```text
AI_Brain/
├── requirements.txt
├── ai_brain.py
└── templates/
    └── index.html
```

### `requirements.txt`
```text
flask
opencv-python
easyocr
ultralytics
```

### Server Environment Setup Commands
*   **Windows Environment:**
    ```cmd
    pip install -r requirements.txt
    ```
*   **Ubuntu/Linux Environment:**
    ```bash
    pip install -r requirements.txt --break-system-packages
    ```

---

## 💻 3. Central AI Brain Server Script (`ai_brain.py`)

Run this script on the central server hub laptop to manage real-time YOLOv8 vehicle filters, EasyOCR text character classification maps, and the Flask frontend dashboard on Port `8080`.

```python
import socket
import cv2
import time
import threading
from datetime import datetime
from flask import Flask, render_template, Response, jsonify
import easyocr

app = Flask(__name__)

global_frame = None
processing_frame = None  
dashboard_data = {
    "current_status": "LANE CLEAR - GATE CLOSED",
    "status_class": "clear",
    "last_plate": "NONE",
    "logs": []
}

reader = easyocr.Reader(['en'], gpu=False)
AUTHORIZED_PLATES = ["MH12HH1234", "GJ01AA9999", "DL3C0001", "MH12HH1245"]
active_vehicles = {}
pi_connection = None  

def ocr_background_worker():
    global processing_frame, dashboard_data, pi_connection, active_vehicles
    
    while True:
        if processing_frame is not None and pi_connection is not None:
            scan_img = processing_frame.copy()
            try:
                ocr_results = reader.readtext(scan_img, paragraph=False)
                detected_plate = "UNKNOWN"
                
                for (bbox, text, prob) in ocr_results:
                    clean_text = "".join(c for c in text if c.isalnum()).upper()
                    if len(clean_text) >= 6:
                        detected_plate = clean_text
                        break
                
                if detected_plate != "UNKNOWN":
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    dashboard_data["last_plate"] = detected_plate
                    
                    if detected_plate in AUTHORIZED_PLATES:
                        pi_connection.sendall(b"OPEN\n")
                        dashboard_data["current_status"] = f"AUTHORIZED: {detected_plate} - OPENING GATE"
                        dashboard_data["status_class"] = "authorized"
                        
                        if detected_plate not in active_vehicles:
                            active_vehicles[detected_plate] = time.time()
                            dashboard_data["logs"].insert(0, {
                                "timestamp": now_str, 
                                "plate": detected_plate, 
                                "type": "AUTHORIZED", 
                                "action": "Vehicle Entered Lane"
                            })
                    else:
                        pi_connection.sendall(b"CLOSE\n")
                        dashboard_data["current_status"] = f"UNAUTHORIZED VEHICLE: {detected_plate}"
                        dashboard_data["status_class"] = "unauthorized"
                        
                        if detected_plate not in active_vehicles:
                            active_vehicles[detected_plate] = time.time()
                            dashboard_data["logs"].insert(0, {
                                "timestamp": now_str, 
                                "plate": detected_plate, 
                                "type": "UNAUTHORIZED", 
                                "action": "Access Denied"
                            })
                else:
                    pi_connection.sendall(b"CLOSE\n")
                    dashboard_data["current_status"] = "LANE CLEAR - GATE CLOSED"
                    dashboard_data["status_class"] = "clear"
                    active_vehicles.clear()
                    
            except Exception as e:
                print(f"OCR Exception: {e}")
                
        time.sleep(1.0)

def video_receiver_worker():
    global global_frame, processing_frame, pi_connection
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 5005))
    server.listen(1)
    print("🚀 NET ENGINE ACTIVE: Listening for Pi Hardware...")

    try:
        conn, addr = server.accept()
        pi_connection = conn
        print(f"✅ LINK OK: Connected to Pi Terminal: {addr}")
        
        cap = cv2.VideoCapture("tcp://192.168.1.20:5000")
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                continue
            global_frame = frame.copy()
            processing_frame = frame.copy()
            
    except Exception as e:
        print(f"❌ Video Receiver error: {e}")
    finally:
        if 'conn' in locals(): conn.close()
        server.close()

@app.route('/')
def index():
    return render_template('index.html')

def generate_video_stream():
    global global_frame
    while True:
        if global_frame is not None:
            ret, jpeg = cv2.imencode('.jpg', global_frame)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
        time.sleep(0.03)

@app.route('/video_feed')
def video_feed():
    return Response(generate_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status_data')
def status_data():
    return jsonify(dashboard_data)

if __name__ == '__main__':
    threading.Thread(target=video_receiver_worker, daemon=True).start()
    threading.Thread(target=ocr_background_worker, daemon=True).start()
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
```

---

## 🍓 4. Edge Hardware Client Script (`gate_client.py`)

Deploy this script directly to the root home directory of the Raspberry Pi (`/home/pi/gate_client.py`). It opens low-latency hardware capture pipelines via native libcamera layers and triggers output relay states.

```python
import socket
import subprocess
import time
import RPi.GPIO as GPIO

GATE_PIN = 18  
LAPTOP_IP = "192.168.1.6"  # Update to target laptop server IP profile

GPIO.setmode(GPIO.BCM)
GPIO.setup(GATE_PIN, GPIO.OUT)
GPIO.output(GATE_PIN, GPIO.LOW)

stream_cmd = "rpicam-vid -t 0 --inline --listen -o tcp://0.0.0.0:5000 --width 640 --height 480 --framerate 30 --codec mjpeg --profile baseline --flush -n"
stream_process = subprocess.Popen(stream_cmd, shell=True)

time.sleep(2) 

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((LAPTOP_IP, 5005))
    print("Successfully linked with Laptop AI Processing Server.")
    
    while True:
        data = client.recv(1024).decode('utf-8')
        if not data:
            break
            
        if "OPEN" in data:
            print("Signal Received: Triggering Relay Open Position!")
            GPIO.output(GATE_PIN, GPIO.HIGH) 
            time.sleep(5)                    
            GPIO.output(GATE_PIN, GPIO.LOW)  
except Exception as e:
    print(f"Network Connection dropped: {e}")
finally:
    stream_process.terminate()
    GPIO.cleanup()
```

---

## 📋 5. System Execution Checklist

### 1. Pre-Deployment Check
Turn on your network provider source (`Rohan WIFI`). Run `ipconfig` (Windows) or `ip route get 1.1.1.1` (Linux) to verify your server laptop IP address coordinates.

### 2. Launch the AI Server Hub
Navigate into your laptop project folder space and boot up your processing loops:
```bash
python ai_brain.py
```
Open your web browser pane and point it to **`http://localhost:8080`** to view your real-time analytics panel.

### 3. Initialize the Edge Client Node
Log into your Raspberry Pi terminal interface via SSH and execute the target hardware client:
```bash
sudo pkill -f rpicam-vid
python3 /home/pi/gate_client.py
```

The system socket layers will immediately bind across the connection. Show your verified plate token image to the lens to witness instant real-time data table appends and hardware relay gate activation!

