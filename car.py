from datetime import datetime
import random
import time
import json

class Car:
    def __init__(self):
        self.timestamp = []
        self.hall_effect_data = []
        self.battery_data = []
        self.temperature_data = []
        self.humidity_data = []
        self.imu_data = []
        self.isDriving = False

    # Return the last N entries or as many entries we have, whichever is lower
    def lastNEntries(self, arr, entries):
        if (len(arr) < entries):
            entries = len(arr)
        return arr[-entries:]

    def storeSensorReadings(self, sensor_readings):
        # Append the new readings to the historic data
        self.timestamp.append(datetime.now().strftime('%H:%M:%S'))
        self.hall_effect_data.append(sensor_readings['hall_effect'])
        self.battery_data.append(sensor_readings['battery'])
        self.temperature_data.append(sensor_readings['temperature'])
        self.humidity_data.append(sensor_readings['humidity'])
        self.imu_data.append(sensor_readings['imu'])

    # Return the last N entries or as many entries we have, whichever is lower
    def lastNEntries(self, arr, entries):
        if (len(arr) < entries):
            entries = len(arr)
        return arr[-entries:]

    # Get the last stores entries as a dictionary
    def readData(self):
        return {
            "timestamp": self.lastNEntries(self.timestamp, 30),
            "hall_effect": self.lastNEntries(self.hall_effect_data, 30),
            "battery": self.lastNEntries(self.battery_data, 30),
            "temperature": self.lastNEntries(self.temperature_data, 30),
            "humidity": self.lastNEntries(self.humidity_data, 30),
            "imu": self.lastNEntries(self.imu_data, 30)
        }

    # Return data to front end for export
    def export_sensor_data(self):
        return {
                "timestamp": self.timestamp,
                "hall_effect": self.hall_effect_data,
                "battery": self.battery_data,
                "temperature": self.temperature_data,
                "humidity": self.humidity_data,
                "imu": self.imu_data
        }

    # Prints to dashboard
    def print_data(self):
        while True:
            json_data = json.dumps(
                {
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'values': {
                        'imu': {
                            'x': self.imu_data[-1][0],
                            'y': self.imu_data[-1][1],
                            'z': self.imu_data[-1][2],
                        },
                        'hef': self.hall_effect_data[-1],
                        'bat': self.battery_data[-1],
                        'tmp': self.temperature_data[-1],
                        'hmd': self.humidity_data[-1],
                    }
                }
            )
            yield f"data:{json_data}\n\n"
            time.sleep(1.5)