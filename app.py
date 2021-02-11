from flask import Flask, render_template, Response, jsonify, request
from car import Car
from random import randint

app = Flask(__name__)
cars = {}
car = Car()

@app.route('/')
def selectCar():
    return render_template("selector.html", cars=cars), 200

@app.route('/debug')
def debugPane():
    return render_template("debug.html", cars=cars), 200

def makeFakeCars(numCars):
    for i in range(numCars):
        car = getOrSetCar(f'Car {i}')
        fake_sensor_string = str(randint(1000000000000, 9999999999999))
        car.storeSensorData(fake_sensor_string)

@app.route('/debug/populate')
def generateFakeCars():
    makeFakeCars(6)
    return '200 OK', 200

@app.route('/dashboard/<carid>')
def carDashboard(carid):
    if (carid not in cars):
        return "That car can't be found. Go back to the dashboard to see currently online cars.", 404
    return render_template("dashboard.html", carid=carid), 200

@app.route('/api/client/<carid>/control')
def controlCar(carid):
    car = cars[carid]
    car.isDriving = request.args.get('driving')
    return '200 OK', 200

@app.route('/api/client/<carid>/data')
def readCarData(carid):
    car = cars[carid]
    data = car.readData()
    return jsonify(data), 200

@app.route('/api/car/<carid>/data', methods=['POST', 'GET'])
def carData(carid):
    car = getOrSetCar(carid)
    if request.method == 'POST':
        sensor_readings = request.get_json()
        car.storeSensorReadings(sensor_readings)
        return '200 OK', 200
    if request.method == 'GET':
        data = car.readData()
        return jsonify(data), 200

@app.route('/api/car/<carid>/control', methods=['GET'])
def getCarIsDriving(carid):
    car = getOrSetCar(carid)
    is_car_driving = car.isDriving
    return jsonify(is_car_driving), 200

def getOrSetCar(carid):
    if (carid not in cars):
        cars[carid] = Car()
    return cars[carid]

# @app.route('/api/car/video_feed')
# def video_feed():
#     return Response(videoFeed.gen(),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/client/<carid>/print/data')
def print_sensor_data(carid):
    car = getOrSetCar(carid)
    return Response(car.print_data(), mimetype='text/event-stream')