
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

    const source = new EventSource('/api/car/print_data');
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
};
