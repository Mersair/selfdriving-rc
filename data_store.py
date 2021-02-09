hall_effect_data = []
battery_data = []
temperature_data = []
humidity_data = []
imu_data = []

# Reads in a sensor data string and logs the data in RAM
def readSensorData(dataStr):
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
    hall_effect_data.append(hall_effect)
    battery_data.append(battery)
    temperature_data.append(temperature)
    humidity_data.append(humidity)
    imu_data.append(imu)


    