#!/bin/bash

#BASEURL="https://ai-car.herokuapp.com"
BASEURL="http://127.0.0.1:5000"
CARID="Pradeeps-Jeep"

while :
do
    echo "Sending sensor data\n"
    echo "Got the response: "
    curl -X POST -H "Content-Type: application/json" \
    -d '{"hall_effect":13.5, "battery":96, "temperature":103.12, "humidity":28, "imu":[0.83, 0.12, 0.91]}' \
    $BASEURL/api/car/$CARID/data
    echo "\n"
    sleep 0.5
    echo "Checking for any start/stop commands\n"
    echo "Got the response: "
    curl $BASEURL/api/car/$CARID/control
    echo "\n"
    sleep 0.5
done