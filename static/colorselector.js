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

function setColors(lower_channels, higher_channels){
    const carid = document.getElementById('car_id').innerText;
    const source_string = "/api/car/" + carid + "/set/color";
    var xhttp = new XMLHttpRequest();
    color_channels = JSON.stringify(
        {
            "lower_channels":lower_channels,
            "higher_channels": higher_channels
        })
//    xhttp.onreadystatechange = function() {
//        if (this.readyState == 4 && this.status == 200) {
//           // Retrieve the sensor data from the car
//           //console.log(xhttp.response);
//        }
//    };
    xhttp.open("POST", source_string, true);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(color_channels);
}

function checkNewHSVMinMax(h, s, v){
    const carid = document.getElementById('car_id').innerText;
    const source_string = "/api/car/" + carid + "/get/color";
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            // Retrieve the sensor data from the car
            json = JSON.parse(xhttp.response);
            console.log(json);
            lower_channels = json.lower_channels;
            higher_channels = json.higher_channels;
            if (h < lower_channels[0]) { lower_channels[0] = h; }
            if (s < lower_channels[1]) { lower_channels[1] = s; }
            if (v < lower_channels[2]) { lower_channels[2] = v; }
            if (h > higher_channels[0]) { higher_channels[0] = h; }
            if (s > higher_channels[1]) { higher_channels[1] = s; }
            if (v > higher_channels[2]) { higher_channels[2] = v; }
            setColors(lower_channels, higher_channels);
        }
    };
    xhttp.open("GET", source_string, true);
    xhttp.send();
}

// taken from https://stackoverflow.com/questions/8022885/rgb-to-hsv-color-in-javascript
function rgb2hsv (r, g, b) {
    let rabs, gabs, babs, rr, gg, bb, h, s, v, diff, diffc, percentRoundFn;
    rabs = r / 255;
    gabs = g / 255;
    babs = b / 255;
    v = Math.max(rabs, gabs, babs),
    diff = v - Math.min(rabs, gabs, babs);
    diffc = c => (v - c) / 6 / diff + 1 / 2;
    percentRoundFn = num => Math.round(num * 100) / 100;
    if (diff == 0) {
        h = s = 0;
    } else {
        s = diff / v;
        rr = diffc(rabs);
        gg = diffc(gabs);
        bb = diffc(babs);

        if (rabs === v) {
            h = bb - gg;
        } else if (gabs === v) {
            h = (1 / 3) + rr - bb;
        } else if (babs === v) {
            h = (2 / 3) + gg - rr;
        }
        if (h < 0) {
            h += 1;
        }else if (h > 1) {
            h -= 1;
        }
    }
    return [Math.round(h * 360), percentRoundFn(s * 100), percentRoundFn(v * 100)]
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
        var pixelData = canvas.getContext('2d').getImageData(ev.offsetX, ev.offsetY, 1, 1).data;
        var hsvArr = rgb2hsv(pixelData[0], pixelData[1], pixelData[2]);
        checkNewHSVMinMax(hsvArr[0], hsvArr[1], hsvArr[2]);
    });
}
