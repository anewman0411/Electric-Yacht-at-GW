import time
import board
import busio
##from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055


i2c = busio.I2C(board.GP1, board.GP0) # gets board.SCL and board.SDA

while not i2c.try_lock(): ## locks sensor before scanning
    pass

# print addresses found once
print("I2C addresses found:", [hex(device_address) for device_address in i2c.scan()])

i2c.unlock() ## unlock sensor once done scannin

sensor_accelerometer = adafruit_bno055.BNO055_I2C(i2c)
print("Sensor check")

a_loop_duration = 60 #seconds
a_loop_interval = 0.5 #seconds

start_time = time.monotonic()
next_run_time = start_time

duration = 60 
end_time = time.monotonic() + duration
next_print = time.monotonic()

while time.monotonic() < end_time:
    current_time = time.monotonic()
    
    if current_time >= next_print:
        data = sensor_accelerometer.linear_acceleration
        print(f"Accel: {data} | Time: {current_time:.2f}")
        
        
        next_print = current_time + 0.5

    time.sleep(0.01)

print("Data collection complete.")
