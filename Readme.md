# 🚗 Smart Parking Gate System

An Edge-AI based automated parking management system that performs real-time vehicle monitoring, license plate recognition, access validation, and automated gate control using Raspberry Pi, EasyOCR, Flask, and Computer Vision.

---

# 📌 Project Overview

The Smart Parking Gate System automates vehicle entry management within a parking facility.

The system:

- Captures live vehicle footage
- Extracts vehicle number plates
- Validates authorized vehicles
- Automatically controls gate access
- Logs entry and access events
- Displays activity on a real-time web dashboard

---

# ✨ Features

- Real-Time Vehicle Monitoring
- License Plate Recognition (LPR)
- Automated Gate Control
- Flask-Based Dashboard
- Raspberry Pi Integration
- Wireless Network Communication
- Entry & Exit Logging
- Edge Computing Implementation

---

# 🛠 Hardware Components

## Edge Node

- Raspberry Pi 4 Model B
- Raspberry Pi Camera Module
- 3.5-inch Touch Display
- Single Channel Relay Module

## Processing Server

- Laptop/Desktop Running Python
- Local Wi-Fi Network Communication

---

# 💻 Software Stack

- Python
- Flask
- OpenCV
- EasyOCR
- Socket Programming
- Raspberry Pi OS

---

# 📂 Project Structure

```text
Smart-Parking-Gate-System/
│
├── README.md
├── requirements.txt
│
├── src/
│   ├── ai_brain.py
│   └── gate_client.py
│
├── templates/
│   └── index.html
│
├── docs/
│   └── deployment_guide.md
│
└── screenshots/
```

---

# ⚙️ System Workflow

```text
Vehicle Arrives
      │
      ▼
Camera Captures Frame
      │
      ▼
Frame Sent to AI Server
      │
      ▼
OCR Reads Number Plate
      │
      ▼
Authorization Verification
      │
 ┌────┴────┐
 │         │
Authorized Unauthorized
 │         │
 ▼         ▼
Open Gate  Access Denied
 │
 ▼
Dashboard Updated
```

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/your-username/Smart-Parking-Gate-System.git
cd Smart-Parking-Gate-System
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run AI Server

```bash
python ai_brain.py
```

## Open Dashboard

```text
http://localhost:8080
```

## Run Raspberry Pi Client

```bash
python3 gate_client.py
```

---

# 📦 Requirements

```text
flask
opencv-python
easyocr
ultralytics
```

Install all dependencies using:

```bash
pip install -r requirements.txt
```

---

# 🧠 Core Modules

## ai_brain.py

Responsible for:

- Video Stream Processing
- License Plate Recognition
- Vehicle Authorization
- Dashboard Updates
- Gate Command Generation

## gate_client.py

Responsible for:

- Camera Streaming
- Socket Communication
- Relay Activation
- Hardware Interface

---

# 📸 Results

Add screenshots in the following section:

## Dashboard

![Dashboard Screenshot](screenshots/dashboard.png)

## Vehicle Detection

![Vehicle Detection](screenshots/detection.png)

## OCR Output

![OCR Output](screenshots/ocr.png)

## Gate Control

![Gate Control](screenshots/gate.png)

---

# 🔮 Future Improvements

- YOLOv8 Vehicle Detection Integration
- Database Management System
- RFID Authentication
- Mobile Application
- Cloud-Based Monitoring
- Multi-Gate Deployment

---

# 🎓 Academic Project

Developed as a B.Tech Final Year Project demonstrating practical implementation of:

- Embedded Systems
- Edge Computing
- Computer Vision
- IoT Automation
- Network Communication

---

# 👨‍💻 Author

**Raj Bari**

Electronics & Telecommunication Engineering

Interested in:

- Embedded Systems
- IoT Solutions
- Computer Vision
- Edge AI
- Industrial earch purposes.
