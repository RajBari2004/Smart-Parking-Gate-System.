import socket
import subprocess
import time
import threading
import RPi.GPIO as GPIO

GATE_PIN = 18  
LAPTOP_IP = "192.168.1.6"  # Target laptop server IP profile
relay_lock = threading.Lock()

# Standard GPIO initialization maps
GPIO.setmode(GPIO.BCM)
GPIO.setup(GATE_PIN, GPIO.OUT)
GPIO.output(GATE_PIN, GPIO.LOW)

print("🎥 Launching native hardware-accelerated MJPEG stream engine...")
# Array execution avoids shell orphaning and process leaks
stream_cmd = [
    "rpicam-vid", "-t", "0", "--inline", "--listen", 
    "-o", "tcp://0.0.0.0:5000", "--width", "640", "--height", "480", 
    "--framerate", "30", "--codec", "mjpeg", "--profile", "baseline", 
    "--flush", "-n"
]
stream_process = subprocess.Popen(stream_cmd)

time.sleep(2) # Allow camera sensor matrices to stabilize stabilization calibration

def trigger_relay_async():
    """Asynchronously drives physical mechanical gate isolation relays without locking network stream reception."""
    # Prevent concurrent cross-firing thread activations
    if not relay_lock.acquire(blocking=False):
        return 
    try:
        print("⚡ [RELAY] Signal Received: Triggering Relay Open Position!")
        GPIO.output(GATE_PIN, GPIO.HIGH)
        time.sleep(5)  # Safe delay duration for vehicle clearance                  
        GPIO.output(GATE_PIN, GPIO.LOW)
        print("🔒 [RELAY] Cooldown Complete: Gate Returned to Lock Position.")
    finally:
        relay_lock.release()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
buffer = ""

try:
    print(f"🔗 Attempting telemetry link-up with AI Server Hub at {LAPTOP_IP}:5005...")
    client.connect((LAPTOP_IP, 5005))
    print("✅ System Core Active: Synchronized across network topology framework.")
   
    while True:
        raw_data = client.recv(1024).decode('utf-8')
        if not raw_data:
            break
        
        buffer += raw_data
        # Process individual commands via custom string token delimiters
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()
            
            if "OPEN" in line:
                # Fire off relay action onto background thread so TCP tracking continues unhindered
                threading.Thread(target=trigger_relay_async, daemon=True).start()
            elif "CLOSE" in line:
                # Only change state if relay isn't actively running an automated open phase
                if not relay_lock.locked():
                    GPIO.output(GATE_PIN, GPIO.LOW)
                    
except Exception as e:
    print(f"❌ Network Connection dropped or server terminated connection: {e}")
finally:
    print("🧹 Cleaning system resources and tearing down streams...")
    try:
        stream_process.terminate()
        stream_process.wait(timeout=2)
    except Exception:
        stream_process.kill() # Hard kill if process resists graceful closure
        
    GPIO.cleanup()
    print("💀 Client processing pipeline shut down cleanly.")
