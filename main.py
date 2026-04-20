import time
import board
import busio
import bitbangio #the i2c0/1 isnt right and were using i2c 0 for both accelerometer and display so we need this to make it work
import adafruit_bno055
import adafruit_gps
import adafruit_pcf8574
import math
import ulab.numpy as numpy
import digitalio
import adafruit_character_lcd.character_lcd as character_lcd

'''time_pin = digitalio.DigitalInOut(board.GPidk)


def get_voltage(time_pin):
    return (time_pin.value * 3.3) / 65535'''



i2c = busio.I2C(board.GP3, board.GP2) # gets board.SCL and board.SDA
lcdi2c = bitbangio.I2C(board.GP7, board.GP6) # gets SCL and SDA for lcd
RX = board.GP1
TX = board.GP0
+++++++++++++++++++++++++++++++++++++++++++
spi = busio.SPI(board.GP14, MOSI=board.GP11, MISO=board.GP12)
cs = digitalio.DigitalInOut(board.GP9)
pcf = adafruit_pcf8574.PCF8574(lcdi2c, address=0x27)

backlight = pcf.get_pin(3)
backlight.switch_to_output(value=True)

lcd = character_lcd.Character_LCD(
    pcf.get_pin(0), pcf.get_pin(2), # rs, en
    pcf.get_pin(4), pcf.get_pin(5), pcf.get_pin(6), pcf.get_pin(7), # d4-d7
    20, 4, # dimensions
)

lcd.backlight = True

import adafruit_sdcard as sdkid
import storage

sdcard = sdkid.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

with open("/sd/test.txt", "w") as f:
    f.write("Hello world!\r\n")
    
with open("/sd/test.txt", "r") as f:
    print("Read line from file:")
    print(f.readline())

uart = busio.UART(TX, RX, baudrate=9600, timeout=0.1, receiver_buffer_size=256)
gps = adafruit_gps.GPS(uart, debug=False)


while not i2c.try_lock(): ## locks sensor before scanning
    pass

# print addresses found once
print("I2C addresses found:", [hex(device_address) for device_address in i2c.scan()])

i2c.unlock() ## unlock sensor once done scannin

sensor_accelerometer = adafruit_bno055.BNO055_I2C(i2c)
print("Sensor check")

gps.send_command(b"PMTK314,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0")
time.sleep(1)
gps.send_command(b'PMTK220,1000')


start_time = time.monotonic()
next_run_time = start_time

duration = 18000
end_time = time.monotonic() + duration
next_print = time.monotonic()
next_debug = time.monotonic()

with open("/sd/acceleration.txt", "a") as f:
    f.write("Acceleration vs. Time\r\n")
    f.write(f"Start time: {start_time}\r\n")
    
with open("/sd/velocity.txt", "w") as f:
    f.write("Velocity vs. Time\r\n")
    f.write(f"Start time: {start_time}\r\n")

last_line_accel = None

while time.monotonic() < end_time:
    
    gps.update()
    
    current_time = time.monotonic()
    
    if current_time >= next_print:
        
        ##accelerometer
        time1 = current_time-start_time
        data_a = sensor_accelerometer.linear_acceleration
        data_a_magnitude = math.sqrt(sensor_accelerometer.linear_acceleration[0]**2 + sensor_accelerometer.linear_acceleration[1]**2 + sensor_accelerometer.linear_acceleration[2]**2)
        data_orient = numpy.array([sensor_accelerometer.euler])
        data_gyro = numpy.array([sensor_accelerometer.gyro])
        data_gravity = numpy.array([sensor_accelerometer.gravity])
        data_orient_gravity = data_orient - data_gravity
        data_orient_degrees = (data_gyro*180)/math.pi
        
        with open("/sd/acceleration.txt", "a") as f:
            f.write(f"Accel: {data_a}, Time: {time1:.2f}\r\n")
            
        with open("/sd/acceleration.txt", "r") as f:
            for line in f:
                last_line = line
                
        if last_line:
            print("Most recent accel:", last_line.strip()) 
            
        ##print(f"Accel: {data_a} | Time: {current_time:.2f}")
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
        
            data_gknt = gps.speed_knots
            data_glat = gps.latitude
            data_glong = gps.longitude
            data_gtime = gps.timestamp_utc
            data_ang = gps.track_angle_deg
        
            print(f"Fix0: {fix0}")
            print(f"Fix1: {fix1}")
            print(f"Date and Time: {datetime}")
        
            ###print(f"Speed: {data_gkmh} kmh")
            print(f"Latitude: {data_glat}")
            print(f"Longitude: {data_glong}")
            print(f"Time: {data_gtime}")
            print(f"Angle: {data_ang}")
            
            with open("/sd/velocity.txt", "a") as f:
                f.write(f"Vel: {data_gknt}, Time: {time1}")
                
            with open("/sd/acceleration.txt", "r") as f:
                for line in f:
                    last_line = line
                    
            if last_line:
                print("Most recent velocity:", last_line.strip())
            
            lcd.clear()
            lcd.message = f"Speed: {data_gknt:.3f} knots\nStart Time: {start_time:.3f}\nCurrent Time : {current_time:.3f}\n"
            
        else:
            data_gkmh = 0.0
            print ("GPS: Waiting for fix... :(")
            print (f"Sats in Use: {gps.satellites}")
        
            lcd.clear()
            lcd.message = f"Start Time: {start_time:.3f}\nCurrent Time : {current_time:.3f}\n"
        
        next_print = current_time + 0.5
    
        

print("Data collection complete.")











