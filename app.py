from flask_socketio import SocketIO
from flask import Flask, render_template, Response, jsonify, request, abort
from car import Car
from random import randint
import json
import uuid
import threading
from redisConn import RedisConn

app = Flask(__name__)
socketio = SocketIO(app)
redis = RedisConn()

# Initialize the cars in the set
initial_cars = {}
redis.set_car_json('cars', json.dumps(initial_cars))
# car = Car()

# Video Socket logging, one namespace for computer vision client and one for the web client
@socketio.on('connect', namespace='/web')
def connect_web():
    print('[INFO] Web client connected: {}'.format(request.sid))


@socketio.on('disconnect', namespace='/web')
def disconnect_web():
    print('[INFO] Web client disconnected: {}'.format(request.sid))


@socketio.on('connect', namespace='/cv')
def connect_cv():
    print('[INFO] CV client connected: {}'.format(request.sid))

@socketio.on('disconnect', namespace='/cv')
def disconnect_cv():
    print('[INFO] CV client disconnected: {}'.format(request.sid))


# Video Socket message handler
@socketio.on('cv2server', namespace='/cv')
def handle_cv_message(message):
    socketio.emit('server2web', message, namespace='/web')


def getCar(car_id):
    car_json = redis.get_car_json(car_id)
    if car_json is None:
        abort(404, description=(f"Your request for car '{car_id}' could not be processed as the car doesn't exist."))
    else:
        return car_json

def setCar(car_id, car_data):
    car_json = json.dumps(car_data)
    redis.set_car_json(car_id, car_json)

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

@app.route('/')
def selectCar():
    cars = redis.get_car_json('cars')
    return render_template("landing.html", cars=cars), 200

@app.route('/api/enroll')
def enrollCar():
    car_id = str(uuid.uuid4())
    initial_configs = {
        "speed": 0,
        "lower_channels": [255, 255, 255],
        "higher_channels": [0, 0, 0]
    }
    setCar(car_id, initial_configs)
    cars = redis.get_car_json('cars')
    cars[car_id] = getFriendlyCarName()
    redis.set_car_json('cars', json.dumps(cars))
    return jsonify({'id': car_id}), 200
    

@app.route('/dashboard/<car_id>')
def carDashboard(car_id):
    cars = redis.get_car_json('cars')
    if (car_id not in cars):
        return "That car can't be found. Go back to the dashboard to see currently online cars.", 404
    return render_template("dashboard.html", carid=car_id), 200

@app.route('/dashboard/<car_id>/colorselector')
def colorSelector(car_id):
    cars = redis.get_car_json('cars')
    if (car_id not in cars):
        return "That car can't be found. Go back to the dashboard to see currently online cars.", 404
    return render_template("colorselector.html", carid=car_id), 200

@app.route('/api/client/<car_id>/control')
def controlCar(car_id):
    cars = redis.get_car_json('cars')
    car = cars[car_id]
    car.isDriving = request.args.get('driving')
    return '200 OK', 200

@app.route('/api/car/<car_id>/control', methods=['POST', 'GET'])
def carControl(car_id):
    car = getCar(car_id)
    if request.method == 'POST':
        accepted_args = ['throttle_speed', 'algorithm', 'algorithm_mode', 'higher_channels', 'lower_channels']
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
def carData(car_id):
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

    if randint(1, 100) == 7:
        ee_names = ['Binky\'s Bus', 'Gordon\'s Granola Gondola', 'Pradeep\'s Jeep']
        return ee_names[randint(0, len(ee_names) - 1)]

    return f"{descriptor} {color} {car}"

@app.route('/api/client/<car_id>/video_feed')
def video_feed(car_id):
    # car = getCar(car_id)
    return Response(car.generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/client/<car_id>/filtered_video_feed')
def filtered_video_feed(car_id):
    # car = getCar(car_id)
    return Response(car.generate_filtered(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/client/<car_id>/print/data')
def print_sensor_data(car_id):
    car_json = getCar(car_id)
    print(car_json)
    return Response(redis.print_data(car_json), mimetype='text/event-stream')

@app.route('/api/client/<car_id>/export/data')
def export_sensor_data(car_id):
    car_json = getCar(car_id)
    return jsonify({
        "timestamp": car_json['timestamp'],
        "hall_effect": car_json['hall_effect_data'],
        "battery": car_json['battery_data'],
        "temperature": car_json['temperature_data'],
        "humidity": car_json['humidity_data'],
        "imu": car_json['imu_data']
    })

@app.route('/api/car/<car_id>/set/speed/<speed>', methods=['POST'])
def set_speed(car_id, speed):
    car_json = redis.get_car_json(car_id)
    car_json['speed'] = speed
    redis.set_car_json(car_id, json.dumps(car_json))
    return '200 OK', 200

@app.route('/api/car/<car_id>/get/speed')
def get_speed(car_id):
    car_json = redis.get_car_json(car_id)
    return json.dumps(car_json['speed'])

@app.route('/api/car/<car_id>/get/color')
def get_color_channels(car_id):
    car_json = redis.get_car_json(car_id)
    return jsonify({
            "lower_channels": car_json['lower_channels'],
            "higher_channels": car_json['higher_channels']
    })

@app.route('/api/car/<car_id>/send/coordinates', methods=['POST'])
def send_coordinates(car_id):
    if request.method == 'POST':
        coordinates = request.get_json()
        car.setColorChannels(coordinates['x'], coordinates['y'], car_id)
        return '200 OK', 200

@app.route('/api/car/<car_id>/reset/color')
def reset_color_channels(car_id):
    car_json = redis.get_car_json(car_id)
    car_json['higher_channels'] = [0, 0, 0]
    car_json['lower_channels'] = [255, 255, 255]
    redis.set_car_json(car_id, car_json)
    return '200 OK', 200

@app.route('/api/car/<car_id>/startup/controls')
def get_startup_controls(car_id):
    car_json = redis.get_car_json(car_id)
    return jsonify({
        "speed": car_json['speed'],
        "lower_channels": car_json['lower_channels'],
        "higher_channels": car_json['higher_channels']
    })
    # t2 = threading.Thread(target=car.startDriving, args=(car.speed, car.lower_channels, car.higher_channels,))
    # t2.daemon = True
    # t2.start()
    # return jsonify(car.getStartupControls())


# check to see if this is the main thread of execution
if __name__ == '__main__':
    # ap = argparse.ArgumentParser()
    # ap.add_argument("-s", "--speed", nargs='?', const=50, type=int, required=True, help="Car Speed")
    # ap.add_argument("-l", "--lowerArr", required=True, help="Lower Color Channel")
    # ap.add_argument("-u", "--higherArr", required=True, help="Higher Color Channel")
    # args = vars(ap.parse_args())
    # print(args["speed"])

    # python program exits when only daemon threads are left

    # start a thread that will perform car camera
    # t = threading.Thread(target=car.detect, args=())
    # t.daemon = True
    # t.start()

    # start the flask app
    print('[INFO] Starting server at http://0.0.0.0:5000')
    socketio.run(app=app, host='0.0.0.0', port=5000)
