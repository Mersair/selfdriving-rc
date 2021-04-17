#!/bin/bash

SERVER_URL="https://ai-car.herokuapp.com"
FLASK_DEBUG_IP="127.0.0.1:5000"
CAR_ID_LOCATION="/etc/selfdriving-rc/car_id"
CAR_SPEED_LOCATION="/etc/selfdriving-rc/car_speed"
CAR_STEERING_LOCATION="/etc/selfdriving-rc/car_steering"
CAR_SENSOR_DATA_LOCATION="/etc/selfdriving-rc/sensor_data"
CAR_DRIVING_PROGRAM="/home/pi/Documents/car/drive.py"

RUNNING_PROCESSES=`lsof -i -P -n | grep $FLASK_DEBUG_IP`

if [ -z $RUNNING_PROCESSES ]; then
echo "No flask debug server found. Connecting to remote server at '$SERVER_URL'."
else
echo "Flask debug server detected. Connecting to '$FLASK_DEBUG_IP'."
SERVER_URL="$FLASK_DEBUG_IP"
fi

echo "Resetting config files and removing any duplicate instances of '$CAR_DRIVING_PROGRAM'"
PROGRAM_FILENAME=`basename $CAR_DRIVING_PROGRAM`
pkill -f $PROGRAM_FILENAME
echo "" > $CAR_ID_LOCATION
echo 0 > $CAR_SPEED_LOCATION
echo "" > $CAR_SENSOR_DATA_LOCATION

sleep 5

stdbuf -o0 cat /dev/ttyACM0 >$CAR_SENSOR_DATA_LOCATION &

echo "Starting selfdriving program in child process"
nohup python3 $CAR_DRIVING_PROGRAM > /home/pi/Documents/car/logs/drive &
DRIVING_SCRIPT_PID=$!

# To be called in order to properly terminate child process
terminate_startup () {
    kill $DRIVING_SCRIPT_PID
    exit $1
}

# Delay to ensure driving code has recieved an ID and updated the /car_id file
sleep 5

echo "Reading car ID from '$CAR_ID_LOCATION'."
CAR_ID=`cat $CAR_ID_LOCATION`
if [ ${#CAR_ID} -eq 36 ]; then
echo "Car is enrolled with the id '$CAR_ID'."
else
echo "ID was malformed. Please ensure '$CAR_DRIVING_PROGRAM' is properly \
setting the file at '$CAR_ID_LOCATION'."
#terminate_startup 0
fi

while :
do
    echo "Reading sensor data\n"
    SENSOR_STRING=`grep . /etc/selfdriving-rc/sensor_data | tail -n 1`
    echo "Sending sensor data\n"
    SENSOR_RESPONSE=`curl -sX POST -H "Content-Type: application/json" \
    -d '{"sensor_string":"$SENSOR_STRING"}' $BASEURL/api/car/$CARID/data`
    if [ "$SENSOR_RESPONSE" == "200 OK" ]; then
    echo "Server ackd sensor data"
    else
    echo "Server is offline, or rejected the sensor data"
    fi
    echo "Checking for car control commands"
    CAR_SPEED=`curl -sX GET $SERVER_URL/api/car/$CAR_ID/get/speed`
    echo "Car speed: $CAR_SPEED"
    CAR_STEERING=`curl -sX GET $SERVER_URL/api/car/$CAR_ID/get/steering`
    echo "Steering intensity: $CAR_STEERING"
    echo $CAR_SPEED > /etc/selfdriving-rc/car_speed
    echo $CAR_STEERING > /etc/selfdriving-rc/car_steering
       
    sleep 3
done