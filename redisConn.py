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

    def store_sensor_readings(self, car_id, car_json, sensor_readings):
        # Append the new readings to the historic data
        sensor_time = datetime.now().strftime('%H:%M:%S')
        car_json["timestamp"].append(sensor_time)
        car_json["hall_effect_data"].append(sensor_readings['hall_effect'])
        car_json["battery_data"].append(sensor_readings['battery'])
        car_json["temperature_data"].append(sensor_readings['temperature'])
        car_json["humidity_data"].append(sensor_readings['humidity'])
        car_json["imu_data"].append(sensor_readings['imu'])
        r.set(car_id, json.dumps(car_json))
        return json.dumps({
            "timestamp": sensor_time,
            "hall_effect_data": sensor_readings["hall_effect"],
            "battery_data": sensor_readings['battery'],
            "temperature_data": sensor_readings['temperature'],
            "humidity_data": sensor_readings['humidity'],
            "imu_data": sensor_readings['imu']
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
            "imu": self.lastNEntries(car_json["imu_data"], 30)
        }

    # Prints to dashboard
    def print_data(self, car_json):
        last_length = 1
        print("------ printing car ------")
        while True:
            if len(car_json['temperature_data']) > last_length:
                last_length = len(car_json['temperature_data'])
                json_data = json.dumps(
                    {
                        'time': datetime.now().strftime('%H:%M:%S'),
                        'values': {
                            'imu': {
                                'x': car_json['imu_data'][-1][0],
                                'y': car_json['imu_data'][-1][1],
                                'z': car_json['imu_data'][-1][2],
                            },
                            'hef': car_json['hall_effect_data'][-1],
                            'bat': car_json['battery_data'][-1],
                            'tmp': car_json['temperature_data'][-1],
                            'hmd': car_json['humidity_data'][-1],
                        }
                    }
                )
                yield f"data:{json_data}\n\n"
            time.sleep(1.0)
