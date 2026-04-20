import time
import board
import busio
import adafruit_bno055
import adafruit_gps
import math
import ulab.numpy as numpy
import digitalio
import adafruit_character_lcd.character_lcd_i2c as character_lcd

RX = board.GP1
TX = board.GP0


i2c_bus = busio.I2C(board.GP3, board.GP2) # gets board.SCL and board.SDA
RX = board.GP13
TX = board.GP12
lcd1_columns = 16
lcd1_rows = 2

'''spi = busio.SPI(board.GP8, MOSI=board.GP10, MISO=board.GP11)
cs = digitalio.DigitalInOut(board.GP12)'''

import adafruit_sdcard as sdkid
import storage

'''sdcard = sdkid.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")'''


uart = busio.UART(TX, RX, baudrate=9600, timeout=30, receiver_buffer_size=256)
gps = adafruit_gps.GPS(uart, debug=False)
gps.send_command(b'PMTK251,115200')
time.sleep(1.0)
uart.deinit()
uart = busio.UART(TX, RX, baudrate=115200, timeout=30, receiver_buffer_size=256)
gps = adafruit_gps.GPS(uart, debug=False)


while not i2c_bus.try_lock(): ## locks sensor before scanning
    pass

# print addresses found once
print("I2C addresses found:", [hex(device_address) for device_address in i2c_bus.scan()])

i2c_bus.unlock() ## unlock sensor once done scanning

lcd1 = character_lcd.Character_LCD_I2C(i2c_bus, lcd1_columns, lcd1_rows)
lcd.color = [100, 0, 0]
lcd.message = "Hello\nCircuitPython"

sensor_accelerometer = adafruit_bno055.BNO055_I2C(i2c_bno)

gps.send_command(b"PMTK314,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0")
time.sleep(1)
gps.send_command(b'PMTK220,1000')

a_loop_duration = 60 #seconds
a_loop_interval = 0.5 #seconds

start_time = time.monotonic()
next_run_time = start_time

duration = 300	 
end_time = time.monotonic() + duration
next_print = time.monotonic()
next_debug = time.monotonic()

while time.monotonic() < end_time:
    
    gps.update()
    
    current_time = time.monotonic()
    
    if current_time >= next_print:
        
        ##accelerometer
        data_a = sensor_accelerometer.linear_acceleration
        data_a_magnitude = math.sqrt(sensor_accelerometer.linear_acceleration[0]**2 + sensor_accelerometer.linear_acceleration[1]**2 + sensor_accelerometer.linear_acceleration[2]**2)
        data_orient = numpy.array([sensor_accelerometer.euler])
        data_gyro = numpy.array([sensor_accelerometer.gyro])
        data_gravity = numpy.array([sensor_accelerometer.gravity])
        data_orient_gravity = data_orient - data_gravity
        data_orient_degrees = (data_gyro*180)/math.pi
        
        print(f"Accel: {data_a} | Time: {current_time:.2f}")
        print(f"Acceleration Magnitude: {data_a_magnitude}")
        print(f"Orientation Og: {data_orient}")
        print(f"Gyro Og: {data_gyro}")
        print(f"Orientation Gravity: {data_orient_gravity}")
        print(f"Orientation Degrees: {data_orient_degrees}")
        
        ##GPS      
        if gps.has_fix:
            fix0 = gps.fix_quality_3d
            fix1 = gps.fix_quality
            datetime = gps.datetime
        
            data_gkmh = gps.speed_kmh
            data_glat = gps.latitude
            data_glong = gps.longitude
            data_gtime = gps.timestamp_utc
            data_ang = gps.track_angle_deg
        
            print(f"Fix0: {fix0}")
            print(f"Fix1: {fix1}")
            print(f"Date and Time: {datetime}")
        
            print(f"Speed: {data_gkmh} kmh")
            print(f"Latitude: {data_glat}")
            print(f"Longitude: {data_glong}")
            print(f"Time: {data_gtime}")
            print(f"Angle: {data_ang}")
        
        next_print = current_time + 0.5
        
    if current_time >= next_debug:
        if not gps.has_fix:
            print ("GPS: Waiting for fix... :(")
            print (f"Sats in Use: {gps.satellites}")
        next_debug = current_time + 30
        

print("Data collection complete.")









