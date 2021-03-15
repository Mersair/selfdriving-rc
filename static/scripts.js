
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
    imuConfig.data.labels.push(data.time);
    imuConfig.data.datasets[0].data.push(data.values.imu.x);
    imuConfig.data.datasets[1].data.push(data.values.imu.y);
    imuConfig.data.datasets[2].data.push(data.values.imu.z);
}

function hefUpdate(data) {
    hefConfig.data.labels.push(data.time);
    hefConfig.data.datasets[0].data.push(data.values.hef);
}

function batUpdate(data) {
    batConfig.data.labels.push(data.time);
    batConfig.data.datasets[0].data.push(data.values.bat);
}

function tmpUpdate(data) {
    tmpConfig.data.labels.push(data.time);
    tmpConfig.data.datasets[0].data.push(data.values.tmp);
}

function hmdUpdate(data) {
    hmdConfig.data.labels.push(data.time);
    hmdConfig.data.datasets[0].data.push(data.values.hmd);
}

function downloadCSV(data, carid){
   let csvContent = "data:text/csv;charset=utf-8,"

   rows = [];
   rows.push(["timestamp", "battery", "hall_effect", "humidity", "imu_x", "imu_y", "imu_z", "temperature"])
   let i;
   sensorData = JSON.parse(data);
   for(i=0; i<sensorData.temperature.length; i++){
        timestamp = sensorData.timestamp[i];
        battery = sensorData.battery[i];
        hall_effect = sensorData.hall_effect[i];
        humidity = sensorData.humidity[i];
        imu_x = sensorData.imu[i][0];
        imu_y = sensorData.imu[i][1];
        imu_z = sensorData.imu[i][2];
        temperature = sensorData.temperature[i];
        rows.push([timestamp, battery, hall_effect, humidity, imu_x, imu_y, imu_z, temperature]);
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

    const download_string = carid + " " + year + "-" + month + "-" + day + " data.csv";
    link.setAttribute("download", download_string);
    document.body.appendChild(link); // Required for FF

    link.click();
}

function startCar(){
    const carid = document.getElementById('car_id').innerText;
    document.getElementById("startCar").hidden = true;
    document.getElementById("stopCar").hidden = false;

    const source_string = "/api/car/" + carid + "/startup/controls";
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

function stopCar(){
    document.getElementById("stopCar").hidden = true;
    document.getElementById("startCar").hidden = false;
}

function exportSensorData(){
    const carid = document.getElementById('car_id').innerText;
    const source_string = "/api/client/" + carid + "/export/data";
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
           // Retrieve the sensor data from the car
           let sensorData = xhttp.response;
           downloadCSV(sensorData, carid);
        }
    };
    xhttp.open("GET", source_string, true);
    xhttp.send();
}

document.addEventListener("DOMContentLoaded", function(event) {
    const image_elem = document.getElementById("streamer-image");

    var socket = io.connect('http://' + document.domain + ':' + location.port + '/web', {
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

    // Update image and text data based on incoming data messages
    socket.on('server2web', (msg) => {
        image_elem.src = msg.image;
    });
});

window.onload = function() {

    const imuContext = document.getElementById('imuChart').getContext('2d');
    const hefContext = document.getElementById('hefChart').getContext('2d');
    const batContext = document.getElementById('batChart').getContext('2d');
    const tmpContext = document.getElementById('tmpChart').getContext('2d');
    const hmdContext = document.getElementById('hmdChart').getContext('2d');

    Chart.defaults.global.defaultFontColor = '#aeaeae';
    const imuChart = new Chart(imuContext, imuConfig);
    const hefChart = new Chart(hefContext, hefConfig);
    const batChart = new Chart(batContext, batConfig);
    const tmpChart = new Chart(tmpContext, tmpConfig);
    const hmdChart = new Chart(hmdContext, hmdConfig);

    const carid = document.getElementById('car_id').innerText;
    const source_string = "/api/client/" + carid + "/print/data";
    const source = new EventSource(source_string);
    let sensorArr = [hefConfig, batConfig, tmpConfig, hmdConfig];
    let chartArr = [imuChart, hefChart, batChart, tmpChart, hmdChart];

    source.onmessage = function (event) {
        const data = JSON.parse(event.data);
        for(let i=0; i<sensorArr.length; i++){
            shiftSensor(sensorArr[i]);
        }
        shiftImuSensor();
        imuUpdate(data);
        hefUpdate(data);
        batUpdate(data);
        tmpUpdate(data);
        hmdUpdate(data);
        for(let i=0; i<chartArr.length; i++){
            chartArr[i].update();
        }
    };

    let slider = document.getElementById("myRange");
    let speed = document.getElementById("speed");
    const speed_string = "/api/car/" + carid + "/get/speed";
    console.log(speed_string)
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
           // Retrieve the speed value from the dashboard
           let speedValue = JSON.parse(xhttp.response);
           speed.innerHTML = speedValue;
           slider.value  = (speedValue/5);
        }
    };
    xhttp.open("GET", speed_string, true);
    xhttp.send();
};
