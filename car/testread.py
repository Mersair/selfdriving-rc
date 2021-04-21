import serial
import time
import requests
import subprocess

time.sleep(7)

ser = serial.Serial('/dev/ttyACM0', 9600)
f = open("/etc/selfdriving-rc/car_id.txt")
car_id = f.readline()
print(car_id)
f.close()

post_url = f"https://ai-car.herokuapp.com/api/car/{car_id}/data"

first_reading = True

# demo_readings_file = open("/home/pi/Documents/car/demo_readings")
# demo_readings = []
# for line in demo_readings_file:
#     demo_readings.append(line)
# line_position = 0

# def getDemoReading():
#     global line_position
#     if line_position == len(demo_readings):
#         line_position = 0
#     demo_reading = demo_readings[line_position]
#     line_position += 1
#     return demo_reading

while True:
    reading = ser.readline()
    if first_reading:
        first_reading = False
        time.sleep(1)
        continue
    try:
        reading = str(reading, 'utf-8')
    except UnicodeDecodeError as e:
        print("UE error")
        continue
    except Exception as e:
        print("General exception")
        continue
    reading = reading.rstrip('\r\n')
    temp_reading = subprocess.run("vcgencmd measure_temp", shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
    temp_reading = temp_reading[5:-3]
    #temp_reading.replace("Distance 1:", "Distance 0:0.00|Distance 1:")
    reading = f"{reading}|cpu_temp:{temp_reading}"
    print(reading)
    myobj = {'sensor_string': reading}
    result = requests.post(post_url, json = myobj)
    print(result.text)

ser.close()