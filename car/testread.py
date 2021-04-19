import serial
import time
import requests

time.sleep(5)

# set up the serial line
ser = serial.Serial('/dev/ttyACM0', 9600)
# url to upload
f = open("/etc/selfdriving-rc/car_id.txt")
car_id = f.readline()
print(car_id)
f.close()

post_url = f"https://ai-car.herokuapp.com/api/car/{car_id}/data"

while True:
    reading = ser.readline()
    reading = str(reading, 'utf-8')
    reading = reading.rstrip('\r\n')
    print(reading)
    myobj = {'sensor_string': reading}
    result = requests.post(post_url, json = myobj)
    print(result.text)
    time.sleep(5)            # wait (sleep) 5 seconds

ser.close()