import os
import time
import json
from dotenv import load_dotenv
from datetime import datetime
import redis

load_dotenv('.env')
r = redis.from_url(os.environ.get("REDIS_URL"))

class RedisConn:
    def __init__(self):
        pass

    def get_car_json(self, car_id):
        return json.loads(r.get(car_id))

    def set_car_json(self, car_id, car_json):
        r.set(car_id, car_json)

    def link_ids(self, socket_id, car_id):
        r.set(socket_id, car_id)

    def remove_car(self, socket_id):
        car_id = r.get(socket_id)
        r.delete(socket_id)
        r.delete(car_id)

    def store_sensor_readings(self, car_id, car_json, sensor_readings):
        # Append the new readings to the historic data
        sensor_time = datetime.now().strftime('%H:%M:%S')
        car_json["timestamp"].append(sensor_time)
        car_json["hall_effect_data"].append(sensor_readings['hall_effect'])
        car_json["battery_data"].append(sensor_readings['battery'])
        car_json["temperature_data"].append(sensor_readings['temperature'])
        car_json["humidity_data"].append(sensor_readings['humidity'])
        car_json["imu_data"].append(sensor_readings['imu'])
        for idx in range(len(sensor_readings['ultrasonic'])):
            if sensor_readings['ultrasonic'][idx] == 0:
                sensor_readings['ultrasonic'][idx] = 100
        car_json["ultrasonic_data"].append(sensor_readings['ultrasonic'])
        r.set(car_id, json.dumps(car_json))
        return json.dumps({
            "timestamp": sensor_time,
            "hall_effect_data": sensor_readings["hall_effect"],
            "battery_data": sensor_readings['battery'],
            "temperature_data": sensor_readings['temperature'],
            "humidity_data": sensor_readings['humidity'],
            "imu_data": sensor_readings['imu'],
            "ultrasonic_data": sensor_readings['ultrasonic']
        })

    def lastNEntries(self, arr, entries):
        if (len(arr) < entries):
            entries = len(arr)
        return arr[-entries:]

    # Get the last stores entries as a dictionary
    def read_data(self, car_json):
        return {
            "timestamp": self.lastNEntries(car_json["timestamp"], 30),
            "hall_effect": self.lastNEntries(car_json["hall_effect_data"], 30),
            "battery": self.lastNEntries(car_json["battery_data"], 30),
            "temperature": self.lastNEntries(car_json["temperature_data"], 30),
            "humidity": self.lastNEntries(car_json["humidity_data"], 30),
            "imu": self.lastNEntries(car_json["imu_data"], 30),
            "ultrasonic": self.lastNEntries(car_json["ultrasonic_data"], 30)
        }
