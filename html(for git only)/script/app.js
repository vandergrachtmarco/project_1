const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

var mymap

const listenToUI = function() {
    knop = document.querySelector(".js-accel-btn");
    knop.addEventListener("click", function() {
        socket.emit("F2B_get_accel_data")
    });
    knop = document.querySelector(".js-gps-btn");
    knop.addEventListener("click", function() {
        socket.emit("F2B_get_GPS_data")
    });
};

const listenToSocket = function() {
    socket.on("connected", function() {
        console.log("verbonden met socket webserver");
    });

    //in stap 2
    socket.on("B2F_return_accel_data", function(jsonObject){
        console.log(jsonObject);
        document.querySelector(".js-accel").innerHTML = jsonObject.accel_data;
        document.querySelector(".js-shock").innerHTML = (jsonObject.shocks + " shocken");
    });

    socket.on("B2F_return_GPS_data", function(jsonObject){
        console.log(jsonObject);

        latitude = jsonObject.latitude
        longitude = jsonObject.longitude

        document.querySelector(".js-lat").innerHTML = (latitude + " graden");
        document.querySelector(".js-long").innerHTML = (longitude + " graden");
        document.querySelector(".js-speed").innerHTML = (jsonObject.speed + " graden");

        mymap.eachLayer(function(layer) {
            mymap.removeLayer(layer);
        });
        LoadTitleLayer();
        var marker = L.marker([latitude, longitude], { title: marker }).addTo(mymap);
    });
};

const LoadTitleLayer = function() {
    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
            maxZoom: 18,
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
                '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
                'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
            id: 'mapbox/streets-v11',
            tileSize: 512,
            zoomOffset: -1
        }).addTo(mymap);
};

document.addEventListener("DOMContentLoaded", function() {
    console.info("DOM geladen");
    document.querySelector(".js-shock").innerHTML = "0 shocken";

    mymap = L.map('mapid').setView([50.84673, 4.35247], 12);

    LoadTitleLayer();
    listenToUI();
    listenToSocket();
});