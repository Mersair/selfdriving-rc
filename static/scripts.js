
let imuContext = null
let hefContext = null
let batContext = null
let tmpContext = null
let hmdContext = null
let uscContext = null
let imuChart = null
let hefChart = null
let batChart = null
let tmpChart = null
let hmdChart = null
let uscChart = null
let sensorArr = []
let chartArr = []

function shiftSensor(configObj) {
    if (configObj.data.labels.length === 15) {
        configObj.data.labels.shift();
        configObj.data.datasets[0].data.shift();
    }
}

function shiftImuSensor() {
    if (imuConfig.data.labels.length === 15) {
        imuConfig.data.labels.shift();
        imuConfig.data.datasets[0].data.shift();
        imuConfig.data.datasets[1].data.shift();
        imuConfig.data.datasets[2].data.shift();
    }
}

function imuUpdate(data) {
    imuConfig.data.labels.push(data.timestamp);
    imuConfig.data.datasets[0].data.push(data.imu_data[0]);
    imuConfig.data.datasets[1].data.push(data.imu_data[1]);
    imuConfig.data.datasets[2].data.push(data.imu_data[2]);
}

function uscUpdate(data) {
    uscConfig.data.datasets[0].data = data.ultrasonic_data
}

function hefUpdate(data) {
    hefConfig.data.labels.push(data.timestamp);
    hefConfig.data.datasets[0].data.push(data.hall_effect_data);
}

function batUpdate(data) {
    batConfig.data.labels.push(data.timestamp);
    batConfig.data.datasets[0].data.push(data.battery_data);
}

function tmpUpdate(data) {
    tmpConfig.data.labels.push(data.timestamp);
    tmpConfig.data.datasets[0].data.push(data.temperature_data);
}

function hmdUpdate(data) {
    hmdConfig.data.labels.push(data.timestamp);
    hmdConfig.data.datasets[0].data.push(data.humidity_data);
}

function downloadCSV(data, name){
   let csvContent = "data:text/csv;charset=utf-8,"

   rows = [];
   rows.push(["timestamp", "battery", "hall_effect", "humidity", "temperature", "imu_x", "imu_y", "imu_z",
        "ultrasonic 1", "ultrasonic 2", "ultrasonic 3", "ultrasonic 4", "ultrasonic 5", "ultrasonic 6", "ultrasonic 7"]);
   let i;
   sensorData = JSON.parse(data);
   for(i=0; i<sensorData.temperature.length; i++){
        timestamp = sensorData.timestamp[i];
        battery = sensorData.battery[i];
        hall_effect = sensorData.hall_effect[i];
        humidity = sensorData.humidity[i];
        temperature = sensorData.temperature[i];
        imu_x = sensorData.imu[i][0];
        imu_y = sensorData.imu[i][1];
        imu_z = sensorData.imu[i][2];
        ultrasonics = sensorData.ultrasonic[i];
        rows.push([timestamp, battery, hall_effect, humidity, temperature, imu_x, imu_y, imu_z, ultrasonics]);
   }

   rows.forEach(function(rowArray) {
        let row = rowArray.join(",");
        csvContent += row + "\r\n";
   });

    var encodedUri = encodeURI(csvContent);
    var link = document.createElement("a");
    link.setAttribute("href", encodedUri)

    var dateObj = new Date();
    var month = dateObj.getUTCMonth() + 1;
    var day = dateObj.getUTCDate();
    var year = dateObj.getUTCFullYear();

    const download_string = name + " " + year + "-" + month + "-" + day + " data.csv";
    link.setAttribute("download", download_string);
    document.body.appendChild(link); // Required for FF

    link.click();
}

function terminate(){
    const carid = document.getElementById('car_id').innerText;

    const source_string = "/api/car/" + carid + "/terminate";
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
           window.open("/", "_self");
        }
    };
    xhttp.open("GET", source_string, true);
    xhttp.send();
}

function startCar(){
    const carid = document.getElementById('car_id').innerText;
    document.getElementById("startCar").hidden = true;
    document.getElementById("stopCar").hidden = false;

    const source_string = "/api/car/" + carid + "/drive";
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
           // Retrieve the speed value from the dashboard
           let output = JSON.parse(xhttp.response);
           console.log(output);
        }
    };
    xhttp.open("GET", source_string, true);
    xhttp.send();
}

function stopCar() {
    const carid = document.getElementById('car_id').innerText;
    document.getElementById("stopCar").hidden = true;
    document.getElementById("startCar").hidden = false;

    const stop_string = "/api/car/" + carid + "/set/speed/0";
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
           updateSpeedSlider(carid);
        }
    };
    xhttp.open("POST", stop_string, true);
    xhttp.send();

    const stop2_string = "/api/car/" + carid + "/stop/drive";
    var xhttp2 = new XMLHttpRequest();
    xhttp2.open("GET", stop2_string, true);
    xhttp2.send();
}

function exportSensorData(){
    const carid = document.getElementById('car_id').innerText;
    const friendly_name = document.getElementById('friendly_name').innerText;
    const source_string = "/api/client/" + carid + "/export/data";
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
           // Retrieve the sensor data from the car
           let sensorData = xhttp.response;
           downloadCSV(sensorData, friendly_name);
        }
    };
    xhttp.open("GET", source_string, true);
    xhttp.send();
}

document.addEventListener("DOMContentLoaded", function(event) {
    const image_elem = document.getElementById("streamer-image");
    const carid = document.getElementById('car_id').innerText;

    var socket = io.connect("https://ai-car.herokuapp.com/web", {
      reconnection: false
    });

    socket.on('connect', () => {
      console.log('Connected');
    });

    socket.on('disconnect', () => {
      console.log('Disconnected');
    });

    socket.on('connect_error', (error) => {
      console.log('Connect error! ' + error);
    });

    socket.on('connect_timeout', (error) => {
      console.log('Connect timeout! ' + error);
    });

    socket.on('error', (error) => {
      console.log('Error! ' + error);
    });

    let image2web_string = 'image2web/' + carid
    socket.on(image2web_string, (msg) => {
        image_elem.src = msg.image;
    });

    let data2web_string = 'data2web/' + carid
    socket.on(data2web_string, (sensor_readings) => {
        const data = JSON.parse(sensor_readings);
        for(let i=0; i<sensorArr.length; i++){
            shiftSensor(sensorArr[i]);
        }
        shiftImuSensor();
        imuUpdate(data);
        uscUpdate(data);
        hefUpdate(data);
        batUpdate(data);
        tmpUpdate(data);
        hmdUpdate(data);
        for(let i=0; i<chartArr.length; i++){
            chartArr[i].update();
        }
    })
});

function updateSpeedSlider(carid) {
    let speedSlider = document.getElementById("speedRange");
    let speed = document.getElementById("speed");
    const speed_string = "/api/car/" + carid + "/get/speed";
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
           // Retrieve the speed value from the dashboard
           let speedValue = JSON.parse(xhttp.response);
           speed.innerHTML = speedValue;
           speedSlider.value  = (speedValue/5);
        }
    };
    xhttp.open("GET", speed_string, true);
    xhttp.send();
}

function updateSteeringSlider(carid){
    let steeringSlider = document.getElementById("steeringRange");
    let steering = document.getElementById("steering");
    const steering_string = "/api/car/" + carid + "/get/steering";
    var xhttp2 = new XMLHttpRequest();
    xhttp2.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
           // Retrieve the speed value from the dashboard
           let steeringValue = JSON.parse(xhttp2.response);
           steering.innerHTML = steeringValue;
           steeringSlider.value  = (steeringValue/5);
        }
    };
    xhttp2.open("GET", steering_string, true);
    xhttp2.send();
}

function updateToggleDirection(carid){
    let directionSwitch = document.getElementById("directionSwitch");
    const direction_string = "/api/car/" + carid + "/get/direction";
    var xhttp3 = new XMLHttpRequest();
    xhttp3.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
           // Retrieve the speed value from the dashboard
           let directionValue = JSON.parse(xhttp3.response);
           if (directionValue == 1) {
              directionSwitch.checked = true
           }
           else {
              directionSwitch.checked = false
           }
        }
    };
    xhttp3.open("GET", direction_string, true);
    xhttp3.send();
}

function enableVideo() {
    const carid = document.getElementById('car_id').innerText;
    document.getElementById("enableVideo").hidden = true;
    document.getElementById("disableVideo").hidden = false;
    document.getElementById("selectColorButton").disabled = false;

    const source_string = "/api/car/" + carid + "/enable/video";
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", source_string, true);
    xhttp.send();
}

function disableVideo() {
    const carid = document.getElementById('car_id').innerText;
    document.getElementById("enableVideo").hidden = false;
    document.getElementById("disableVideo").hidden = true;
    document.getElementById("selectColorButton").disabled = true;

    const source_string = "/api/car/" + carid + "/disable/video";
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", source_string, true);
    xhttp.send();
}

function updateVideo(carid) {
    const video_string = "/api/car/" + carid + "/get/stream";
    var xhttp4 = new XMLHttpRequest();
    xhttp4.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
           // Retrieve the speed value from the dashboard
           let is_streaming = JSON.parse(xhttp4.response);
           if (is_streaming) {
              enableVideo();
           }
           else {
              disableVideo();
           }
        }
    };
    xhttp4.open("GET", video_string, true);
    xhttp4.send();
}

window.onload = function() {
    imuContext = document.getElementById('imuChart').getContext('2d');
    uscContext = document.getElementById('uscChart').getContext('2d');
    hefContext = document.getElementById('hefChart').getContext('2d');
    batContext = document.getElementById('batChart').getContext('2d');
    tmpContext = document.getElementById('tmpChart').getContext('2d');
    hmdContext = document.getElementById('hmdChart').getContext('2d');

    Chart.defaults.global.defaultFontColor = '#aeaeae';
    imuChart = new Chart(imuContext, imuConfig);
    uscChart = new Chart(uscContext, uscConfig);
    hefChart = new Chart(hefContext, hefConfig);
    batChart = new Chart(batContext, batConfig);
    tmpChart = new Chart(tmpContext, tmpConfig);
    hmdChart = new Chart(hmdContext, hmdConfig);

    sensorArr = [hefConfig, batConfig, tmpConfig, hmdConfig];
    chartArr = [imuChart, uscChart, hefChart, batChart, tmpChart, hmdChart];

    const carid = document.getElementById('car_id').innerText;
    updateVideo(carid);
    updateSpeedSlider(carid);
    updateSteeringSlider(carid);
    updateToggleDirection(carid);
};
