function resetColors(){
    const carid = document.getElementById('car_id').innerText;
    const source_string = "/api/car/" + carid + "/reset/color";
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
           // Retrieve the sensor data from the car
           console.log(JSON.parse(xhttp.response));
        }
    };
    xhttp.open("GET", source_string, true);
    xhttp.send();
}

function sendCoordinates(x, y){
    const carid = document.getElementById('car_id').innerText;
    const source_string = "/api/car/" + carid + "/send/coordinates";
    var xhttp = new XMLHttpRequest();
    coordinates = JSON.stringify(
        {
            "x": x,
            "y": y
        })
    xhttp.open("POST", source_string, true);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(coordinates);
}

window.onload = function(){
    image = document.getElementById("clickImage");
    image.addEventListener("click", function(ev) {
        var x = ev.clientX;
        var y = ev.clientY;
        var canvas = document.createElement('canvas');
        canvas.width = image.width;
        canvas.height = image.height;
        canvas.getContext('2d').drawImage(image, 0, 0, image.width, image.height);
        sendCoordinates(ev.offsetX, ev.offsetY);
    });
}
