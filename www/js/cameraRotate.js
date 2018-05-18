var urls = ['http://192.168.1.122:8080/', 'http://192.168.1.93:8080/video','http://192.168.1.35:8080/video', 'http://admin:SG9uZGExMjU=@192.168.1.64:8080/stream/video/mjpeg'];
var pos = 0;

function Start() {

    next();

    setInterval(next, 5000); // every 5 seconds
}


function next() {
    if (pos == urls.length) pos = 0; // reset the counter
    document.getElementById('rotate').src = urls[pos];
    pos++;
}
