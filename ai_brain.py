import socket
import cv2
import time
import threading
from datetime import datetime
from flask import Flask, render_template, Response, jsonify
import easyocr

app = Flask(__name__)

global_frame = None
processing_frame = None  # Dedicated background slot for OCR scanning
dashboard_data = {
    "current_status": "LANE CLEAR - GATE CLOSED",
    "status_class": "clear",
    "last_plate": "NONE",
    "logs": []
}

# Initialize the text recognition engine
reader = easyocr.Reader(['en'], gpu=False)
AUTHORIZED_PLATES = ["MH12HH1234", "GJ01AA9999", "DL3C0001", "MH12HH1245"]
active_vehicles = {}
pi_connection = None  # Global holder for the Pi communication socket

def ocr_background_worker():
    """Independent background loop dedicated solely to text parsing tasks"""
    global processing_frame, dashboard_data, pi_connection, active_vehicles
    
    while True:
        if processing_frame is not None and pi_connection is not None:
            # Take a snapshot of the current frame to process
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
                print(f"OCR Thread minor glitch: {e}")
                
        # Sample the video feed once per second to ensure zero video lag
        time.sleep(1.0)

def video_receiver_worker():
    """Dedicated video loop to keep the camera feed smooth and responsive"""
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
        
        cap = cv2.VideoCapture("tcp://192.168.1.10:5000")
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                continue
            
            # Instantly mirror the camera frame to the dashboard window
            global_frame = frame.copy()
            # Push the frame to the background scanner without pausing the video
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
        time.sleep(0.03) # Clean ~30 FPS playback delivery configuration

@app.route('/video_feed')
def video_feed():
    return Response(generate_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status_data')
def status_data():
    return jsonify(dashboard_data)

if __name__ == '__main__':
    # Launch both background workers independently
    threading.Thread(target=video_receiver_worker, daemon=True).start()
    threading.Thread(target=ocr_background_worker, daemon=True).start()
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)

