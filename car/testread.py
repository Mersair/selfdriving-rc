import serial
import time
import requests
import subprocess

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
    temp_reading = subprocess.run("vcgencmd measure_temp", shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
    temp_reading = temp_reading[5:-2]
    reading = f"{reading}|cpu_temp:{temp_reading}"
    print(reading)
    myobj = {'sensor_string': reading}
    result = requests.post(post_url, json = myobj)
    print(result.text)

ser.close()