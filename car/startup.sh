#!/bin/bash

SERVER_URL="https://ai-car.herokuapp.com"
FLASK_DEBUG_IP="127.0.0.1:5000"

RUNNING_PROCESSES=`lsof -i -P -n | grep $FLASK_DEBUG_IP`

if [ -z $RUNNING_PROCESSES ]; then
echo "No flask debug server found. Connecting to remote server at '$SERVER_URL'.\n"
else
echo "Flask debug server detected. Connecting to '$FLASK_DEBUG_IP'."
SERVER_URL="$FLASK_DEBUG_IP"
fi

while :
do
    echo "Sending sensor data\n"
    UPLOAD_RESPONSE=`curl -sX POST -H "Content-Type: application/json" \
    -d '{"hall_effect":13.5, "battery":96, "temperature":103.12, "humidity":28, "imu":[0.83, 0.12, 0.91]}' \
    $BASEURL/api/car/$CARID/data`
    if [ "$UPLOAD_RESPONSE" == "200 OK" ]; then
    echo "Server ackd sensor data"
    else
    echo "Server is offline, or rejected the sensor data"
    fi
    sleep 0.5curl -sX POST -H "Content-Type: application/json" \
    -d '{"hall_effect":13.5, "battery":96, "temperature":103.12, "humidity":28, "imu":[0.83, 0.12, 0.91]}' \
    $BASEURL/api/car/$CARID/data
    echo "Checking for any start/stop commands\n"
    CAR_IS_RUNNING_RESPONSE=`curl $BASEURL/api/car/$CARID/control`
    if [ "$CAR_IS_RUNNING_RESPONSE" == "true" ]; then
    echo "Car is set to driving"
    else
    echo "Car is not set to driving"
    fi
    sleep 0.5
done