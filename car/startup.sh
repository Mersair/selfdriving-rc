#!/bin/bash

curl -X POST -H "Content-Type: application/json" \
-d '{"ultrasonic_1":13.5, "temp": 88.1, "imu":[0.83, 0.12, 0.91]}' \
https://ai-car.herokuapp.com/api/car/1/sensordata/upload
