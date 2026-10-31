Here is your complete, step-by-step Master Command Cheat Sheet to easily carry, assemble, and launch your automated smart parking project in front of the B.Tech evaluation board.

📡 STEP 1: Pre-Deployment Network Check (On Your Laptop)

Before powering on anything, turn on your mobile hotspot or portable router named Rohan WIFI.
Open a terminal on your Ubuntu Laptop (Ctrl + Alt + T) and run this command to find your laptop's current network IP address:
bash
ip route get 1.1.1.1 | awk '{print $7}'
Use code with caution.
(Write this number down—for example: 192.168.1.6).

🍓 STEP 2: Boot and Find the Pi's IP (On Your Laptop)

Plug the power cable into your Raspberry Pi. Give it 45 seconds to boot up silently and join your hotspot.
To find the Raspberry Pi's newly assigned network IP address, run this command in your laptop terminal:
bash
ip neighbor show
Use code with caution.
(Look for the active device entry in the list—for example: 192.168.1.20).

💻 STEP 3: Launch the Laptop AI Server Backend

In your laptop terminal, update your ai_brain.py file to point to the Pi's active IP address from Step 2, then run the engine:
bash
cd ~/Desktop/AI_Brain && python3 ai_brain.py
Use code with caution.
• What to do next: Open Google Chrome or Firefox and navigate straight to: http://localhost:8080 to display your live project presentation dashboard.

🔌 STEP 4: Connect to the Pi and Trigger the Camera Client

Open a brand new terminal tab on your laptop (Ctrl + Shift + T) to securely connect inside the Pi over the air and start the camera stream:
1. Log in via SSH:bash
ssh pi@<YOUR_PI_IP_FROM_STEP_2>
Use code with caution.
(Type yes if prompted, then type password 1234).
2. Verify your laptop IP target inside the script matches Step 1:bash
nano /home/pi/gate_client.py
Use code with caution.
(Check that RESET_IP or LAPTOP_IP matches your current laptop IP. Press Ctrl + X to exit).
3. Clear background camera processes and trigger the pipeline:bash
sudo pkill -f rpicam-vid
python3 /home/pi/gate_client.py
Use code with caution.
The link will lock into place instantly! Your dashboard browser window will pop open with the live video feed stream right next to your automated entries/exits history logging table rows.

🛑 STEP 5: Safe Presentation Shutdown Sequence

When your presentation is finished, do not pull the power plug out abruptly. Run these commands to close the project safely:
1. Stop the Laptop Server: Click on your laptop terminal tab running ai_brain.py and press Ctrl + C.
2. Stop the Pi Client: Click on your SSH tab running gate_client.py and press Ctrl + C.
3. Safe Power-Off for the Pi: Inside your Pi SSH prompt, run this command:bash
sudo poweroff
Use code with caution.
(Wait 10 seconds until the green activity light on the Pi stops flashing completely, then unplug the power cord safely).
You are fully prepared to run the entire project manually! Would you like me to write a short text script summarizing the exact talking points you can say to explain the code architecture to the examiners?

