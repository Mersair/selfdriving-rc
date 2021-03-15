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



    # Prints to dashboard
    def print_data(self, car_json):
        last_length = 0
        car = json.loads(car_json)
        while True:
            if not r.exists('temperature_data'):
                continue
            if len(car['temperature_data']) > last_length:
                last_length = len(car['temperature_data'])
                json_data = json.dumps(
                    {
                        'time': datetime.now().strftime('%H:%M:%S'),
                        'values': {
                            'imu': {
                                'x': car['imu_data'][-1][0],
                                'y': car['imu_data'][-1][1],
                                'z': car['imu_data'][-1][2],
                            },
                            'hef': car['hall_effect_data'][-1],
                            'bat': car['battery_data'][-1],
                            'tmp': car['temperature_data'][-1],
                            'hmd': car['humidity_data'][-1],
                        }
                    }
                )
                yield f"data:{json_data}\n\n"
            time.sleep(1.5)