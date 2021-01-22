class Car:
    def __init__(self):
        self.hall_effect_data = []
        self.battery_data = []
        self.temperature_data = []
        self.humidity_data = []
        self.imu_data = []
        self.isDriving = False

    def storeSensorData(self, dataStr):
        # Splice strings to get data
        #TODO: Read these as substrings following the corresponding tag rather than fixed points
        hall_effect = dataStr[0:2]
        battery = dataStr[2:5]
        temperature = dataStr[5:7]
        humidity = dataStr[7:9]
        imu_x = dataStr[9:10]
        imu_y = dataStr[10:11]
        imu_z = dataStr[11:12]
        imu = [imu_x, imu_y, imu_z] #Bundle in an array for similar storage as with other values

        # Append the new readings to the historic data
        self.hall_effect_data.append(hall_effect)
        self.battery_data.append(battery)
        self.temperature_data.append(temperature)
        self.humidity_data.append(humidity)
        self.imu_data.append(imu)

    # Get the last stores entries as a dictionary
    def readData(self):
        return {
            "hall_effect": lastNEntries(self.hall_effect_data, 30),
            "battery": lastNEntries(self.battery_data, 10),
            "temperature": lastNEntries(self.temperature_data, 30),
            "humidity": lastNEntries(self.humidity_data, 30),
            "imu": lastNEntries(self.imu_data, 30)
        }

    # Return the last N entries or as many entries we have, whichever is lower
    def lastNEntries(arr, entries):
        if (sizeof(arr) < entries):
            entries = sizeof(arr)
        return arr[-entries:]