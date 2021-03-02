from flask import Flask, render_template, Response, jsonify, request
from car import Car
from testrun import Testrun
import threading
import argparse

app = Flask(__name__)
cars = {}
car = Car()

@app.route('/')
def selectCar():
    return render_template("landing.html", cars=cars), 200

@app.route('/debug')
def debugPane():
    return render_template("debug.html", cars=cars), 200

def makeFakeCars(numCars):
    for i in range(numCars):
        car_id = len(cars) + 1
        car = getOrSetCar(f'Car {car_id}')
        fake_sensor_readings = {"hall_effect":13.5, "battery":96, "temperature":103.12, "humidity":28, "imu":[0.83, 0.12, 0.91]}
        car.storeSensorReadings(fake_sensor_readings)

@app.route('/debug/populate')
def generateFakeCars():
    num_fake_cars = int(request.args.get('cars'))
    makeFakeCars(num_fake_cars)
    return render_template("debug.html", cars=cars), 200

@app.route('/dashboard/<carid>')
def carDashboard(carid):
    if (carid not in cars):
        return "That car can't be found. Go back to the dashboard to see currently online cars.", 404
    return render_template("dashboard.html", carid=carid), 200

@app.route('/dashboard/<carid>/colorselector')
def colorSelector(carid):
    if (carid not in cars):
        return "That car can't be found. Go back to the dashboard to see currently online cars.", 404
    return render_template("colorselector.html", carid=carid), 200

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

@app.route('/api/client/<carid>/video_feed')
def video_feed(carid):
    car = getOrSetCar(carid)
    return Response(car.generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/client/<carid>/filtered_video_feed')
def filtered_video_feed(carid):
    car = getOrSetCar(carid)
    return Response(car.generate_filtered(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/client/<carid>/print/data')
def print_sensor_data(carid):
    car = getOrSetCar(carid)
    return Response(car.print_data(), mimetype='text/event-stream')

@app.route('/api/client/<carid>/export/data')
def export_sensor_data(carid):
    car = getOrSetCar(carid)
    return jsonify(car.export_sensor_data())

@app.route('/api/car/<carid>/speed/<speed>')
def get_speed(carid, speed):
    car = getOrSetCar(carid)
    return car.getAndSetSpeed(speed)

@app.route('/api/car/<carid>/get/color')
def get_color_channels(carid):
    car = getOrSetCar(carid)
    return jsonify(car.getColorChannels())

@app.route('/api/car/<carid>/set/color', methods=['POST'])
def set_color_channels(carid):
    car = getOrSetCar(carid)
    if request.method == 'POST':
        color_channels = request.get_json()
        car.setColorChannels(color_channels['lower_channels'], color_channels['higher_channels'])
        return '200 OK', 200

@app.route('/api/car/<carid>/reset/color')
def reset_color_channels(carid):
    car = getOrSetCar(carid)
    return car.resetColorChannels()

# check to see if this is the main thread of execution
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--speed", nargs='?', const=50, type=int, action='store', required=True)
    args = vars(ap.parse_args())
    print(args["speed"])

    # start a thread that will perform motion detection
    t = threading.Thread(target=car.detect, args=(args["speed"],))
    t.daemon = True
    t.start()
    # start the flask app
    app.run(debug=True, threaded=True, use_reloader=False)

# release the video stream pointer
car.vs.stop()
