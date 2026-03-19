#boot file is all gemini code for now until we figure out what we want to do with storage and output

import board
import digitalio
import storage
import time

# 1. SETUP THE ONBOARD LED
# board.LED refers to the built-in LED on your Pico W
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# 2. THE POWER-ON "HEARTBEAT"
# This gives the team a visual signal that the code is actually running.
print("--- BOOTING E-YACHT TELEMETRY SYSTEM ---")
for i in range(5):
    led.value = True
    time.sleep(0.05)
    led.value = False
    time.sleep(0.05)

# 3. STORAGE SETTINGS (Optional but helpful)
# If you ever want to save data logs to the Pico's memory, 
# you would configure those permissions here. 
# For now, we'll leave the Pico "Writable" by your laptop.
# storage.remount("/", False) 

print("Boot sequence complete. Transferring control to main.py...")
