from flask import Flask, render_template, Response, jsonify, request, abort
from car import Car
from random import randint
import os
import redis
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('.env')

app = Flask(__name__)
r = redis.from_url(os.environ.get("REDIS_URL"))

# Initialize the cars in the set
initial_cars = {}
r.set('cars', json.dumps(initial_cars))

def getCar(car_id):
    car_json = r.get(car_id)
    if car_json is None:
        abort(404, description=(f"Your request for car '{car_id}' could not be processed as the car doesn't exist."))
    else:
        car = json.loads(car_json)
        return car

def setCar(car_id, car_data):
    car_json = json.dumps(car_data)
    r.set(car_id, car_json)

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

@app.route('/')
def selectCar():
    cars = json.loads(r.get('cars'))
    return render_template("selector.html", cars=cars), 200

@app.route('/api/enroll')
def enrollCar():
    car_id = str(uuid.uuid4())
    setCar(car_id, "{}")
    cars = json.loads(r.get('cars'))
    cars[car_id] = getFriendlyCarName()
    r.set('cars', json.dumps(cars))
    return jsonify({'id': car_id}), 200
    

@app.route('/dashboard/<car_id>')
def carDashboard(car_id):
    cars = json.loads(r.get('cars'))
    if (car_id not in cars):
        return "That car can't be found. Go back to the dashboard to see currently online cars.", 404
    return render_template("dashboard.html", carid=car_id), 200

@app.route('/api/car/<car_id>/control', methods=['POST', 'GET'])
def carControl(car_id):
    car = getCar(car_id)
    if request.method == 'POST':
        accepted_args = ['throttle_speed', 'algorithm', 'algorithm_mode', 'lane_color_high', 'lane_color_low']
        for argument in request.args:
            print(f"Attempting to match the argument named '{argument}'.")
            if argument in accepted_args:
                print(f"Setting the value '{argument}' to '{request.args.get(argument)}'.")
                car[argument] = request.args.get(argument)
        setCar(car_id, car)
        return '200 OK', 200
    if request.method == 'GET':
        return jsonify(car), 200

@app.route('/api/car/<car_id>/data', methods=['POST', 'GET'])
def carData(carid):
    car = getCar(car_id)
    if request.method == 'POST':
        sensor_readings = request.get_json()
        return '200 OK', 200
    if request.method == 'GET':
        data = car.readData()
        return jsonify(data), 200

def getFriendlyCarName():
    descriptors = ['Rusty', 'Shiny', 'Squeaky', 'Leaky', 'New', 'Speedy', 'Sluggish', 'Electric', 'Hybrid', 'Classic', 'Sporty', 'Used']
    colors = ['Red', 'Green', 'Turquoise', 'Yellow', 'Blue', 'Bergundy', 'Gray', 'White', 'Black', 'Hot-pink', 'Tan']
    cars = ['Jeep', '4x4', 'Dually', 'Horse-Drawn Carriage', 'Tricycle', 'Hatchback', 'Van', 'Sedan', 'Civic', 'Bus', 'Tractor']

    descriptor = descriptors[randint(0, len(descriptors) - 1)]
    color = colors[randint(0, len(colors) - 1)]
    car = cars[randint(0, len(cars) - 1)]

    if randint(1, 100) >= 50:
        ee_names = ['Binky\'s Bus', 'Gordon\'s Granola Gondola', 'Pradeep\'s Jeep']
        return ee_names[randint(0, len(ee_names) - 1)]

    return f"{descriptor} {color} {car}"