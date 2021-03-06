#!/bin/bash

#BASEURL="https://ai-car.herokuapp.com"
BASEURL="http://127.0.0.1:5000"
CARID="Pradeeps-Jeep"

while :
do
    curl -X POST -H "Content-Type: application/json" \
    -d '{"hall_effect":13.5, "battery":96, "temperature":103.12, "humidity":28, "imu":[0.83, 0.12, 0.91]}' \
    $BASEURL/api/car/$CARID/data
    echo "\n"
    sleep 1
done