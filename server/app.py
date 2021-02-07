from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
from car import Car

app = Flask(__name__)
cars = {}

@app.route('/')
def selectCar():
    return render_template("selector.html", cars=cars.keys()), 200

@app.route('/dashboard/<carid>')
def versionInfo(carid):
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

@app.route('/api/car/<carid>/set/data')
def storeCarData(carid):
    sensorData = request.args.get('sensordata')
    car = getOrSetCar(carid)
    car.storeSensorData(sensorData)
    return '200 OK', 200

@app.route('/api/car/<carid>/control')
def getCarIsDriving(carid):
    car = getOrSetCar(carid)
    return car.isDriving, 200

def getOrSetCar(carid):
    if (carid not in cars):
        cars[carid] = Car()
    
    return cars[carid]
        