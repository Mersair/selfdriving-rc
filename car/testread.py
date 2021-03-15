import serial
import time

# set up the serial line
ser = serial.Serial('/dev/ttyACM0', 9600)
# Read and record the data
for i in range(50):
    print(ser.readline())
    time.sleep(0.1) # wait (sleep) 0.1 seconds

ser.close()