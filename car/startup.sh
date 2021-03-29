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
    echo "Collecting sensor data\n"
    SENSOR_READING=`cat /dev/ttyACM0 9600`
    echo "Sending sensor data\n"
    UPLOAD_RESPONSE=`curl -sX POST -H "Content-Type: application/json" \
    -d '{"sensor_string":$SENSOR_READING}' $BASEURL/api/car/$CARID/data`
    if [ "$UPLOAD_RESPONSE" == "200 OK" ]; then
    echo "Server ackd sensor data"
    else
    echo "Server is offline, or rejected the sensor data"
    fi
    echo "Checking for any start/stop commands\n"
    CAR_SPEED = `curl -sX GET $SERVER_URL/api/speed | jq -r '.speed'`
    COLOR_RESPONSE = `curl -sX GET $SERVER_URL/api/color_channels`
    CAR_COLOR_HIGH = `echo $COLOR_RESPONSE | jq -r '.upper_channel'`
    CAR_COLOR_LOW = `echo $COLOR_RESPONSE | jq -r '.lower_channel'`
    echo $CAR_SPEED > /etc/selfdriving-rc/car_speed
    echo "$CAR_COLOR_LOW\n$CAR_COLOR_HIGH" > /etc/selfdriving-rc/car_color
    if [ $CAR_SPEED -lt 0 ]; then
    if [ $IS_DRIVING = 0 ] then
    echo "Car speed is now greater than zero. Starting driving script."
    IS_DRIVING = 1
    DRIVING_SCRIPT_PID = `python3 driving.py &`
    fi
    else
    if [ $IS_DRIVING -ge 1 ] then
    echo "Car speed is now zero. Ending driving script."
    IS_DRIVING = 0
    kill $DRIVING_SCRIPT_PID
    fi
    fi
    sleep 0.5
done