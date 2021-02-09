from flask import Flask, render_template, Response, jsonify, request
from car import Car
from videoFeed import VideoFeed

app = Flask(__name__)
cars = {}
videoFeed = VideoFeed()
car = Car()

@app.route('/')
def selectCar():
    return render_template("selector.html", cars=cars.keys()), 200

@app.route('/debug')
def debugPane():
    return render_template("debug.html", cars=cars), 200

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

# @app.route('/api/car/video_feed')
# def video_feed():
#     return Response(videoFeed.gen(),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/car/print_data')
def sensor_data():
    return Response(car.gen(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2204, threaded=True, debug=True)