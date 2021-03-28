#!/bin/bash

SERVER_URL="https://ai-car.herokuapp.com"
FLASK_DEBUG_IP="127.0.0.1:5000"

RUNNING_PROCESSES=`lsof -i -P -n | grep $FLASK_DEBUG_IP`

if [ -z $RUNNING_PROCESSES ]; then
echo "No flask debug server found. Connecting to remote server at '$SERVER_URL'."
else
echo "Flask debug server detected. Connecting to '$FLASK_DEBUG_IP'."
SERVER_URL="$FLASK_DEBUG_IP"
fi

echo "Attempting to enroll car"
ENROLL_RESPONSE=`curl -sX GET $SERVER_URL/api/enroll | jq -r '.id'`
if [ ${#ENROLL_RESPONSE} -ge 36 ]; then
echo "Enrolled succesfully with the id '$ENROLL_RESPONSE'"
echo $ENROLL_RESPONSE > /etc/selfdriving-rc/car_id
else
echo "Could not enroll car. Please ensure server is online."
exit 1
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
    CAR_SPEED = `echo $CONTROL_RESPONSE | jq -r '.speed'`
    CAR_COLOR_HIGH = `echo $CONTROL_RESPONSE | jq -r '.upper_channel'`
    CAR_COLOR_LOW = `echo $CONTROL_RESPONSE | jq -r '.lower_channel'`
    echo $CAR_SPEED > /etc/selfdriving-rc/car_speed
    echo "$CAR_COLOR_LOW\n$CAR_COLOR_HIGH" > /etc/selfdriving-rc/car_color
    sleep 0.5
done