import time
import board
import busio
import digitalio
import gc
#import individual .py files defensively (if they are unfinished or some components not plugged in it will still run)
#these import variable names can be changed if needed but will need to be changed everywhere
try:
    from Telemetry.gps import YachtGPS
    from Telemetry.motor_controller import CurtisController
    from Telemetry.accelerometer import Orientation
    from Telemetry.battery_reader import EnervolBattery
    print("Success: All telemetry modules found.")
except ImportError as e:
    print(f"Warning: Some modules missing {e}")
    #then we create dummy placeholders so it doesnt break
    #HOWEVER CURRENTLY THIS WILL SET ALL TO NONE IF ONLY ONE BREAKS BUT IM NOT GOING TO WRITE A BUNCH OF IF ELSE FOR LOOP ETC RN
    YachtGPS = CurtisController = Orientation = EnervolBattery = None
    
def main():
    print("--- CIRCUITPYTHON YACHT SYSTEM INITIALIZING BEEP BEEP BOOP ---")
    #hardware bus init
    try:
        #I2C from BNO055
        i2c_bus = busio.I2C(board.SCL, board.SDA)
        
        #UART for GPS and maybe battery (board .tx/rx usually gp0 gp1 on pico)
        uart_gps = busio.UART(board.TX, board.RX, baudrate=9600)
    except Exception as e:
        print(f"Hardware Pipe Error: {e}")
        i2c_bus = uart_gps = None
    # component init (turn on each sensor object and wrap individual so one bad sensor doesnt break it)
    
    #setup GPS
    try:
        gps_system = YachtGPS(uart_gps) if YachtGPS else None
    except:
        gps_system = None
        print("GPS Hardware Init Failed :(")
    
    #setup ESC
    try:
        motor_system = CurtisController() if CurtisController else None
    except:
        motor_system = None
        print("Curtis Controller Init Failed which is lowkey bad")
    
    print("Components Initialized. Starting Master Loop...")

    #the master loop!
    while True:
        #gather data only if sensor successfully setup
        #speed over ground from gps
        current_speed = gps_system.get_speed() if gps_system else 0.0
        #RPM and temp from Curtis
        m_rpm = motor_system.get_rpm() if motor_system else 0
        m_temp = motor_system.get_temp() if motor_system else 0
        
        #step 2 doing calculations
        #this ill do later
        
        #step 3 output to dashboard
        #for now just go to console
        print(f"Vessel Speed: {current_speed} kn | RPM: {m_rpm} | Motor Temp: {m_temp}C"
        #step 4 general housekeeping
        gc.collect() #this should clear old data to prevent memory leak
        time.sleep(0.5) #run twice a second which we can change of course
              
#start the program!
    if __name__ == "__main__":
        main()