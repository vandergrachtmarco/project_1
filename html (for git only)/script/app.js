const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

var mymap

const listenToUI = function() {
    knop = document.querySelector(".js-accel-btn");
    if (knop) {
        knop.addEventListener("click", function() {
            socket.emit("F2B_get_accel_data")
        });
    }

    knop = document.querySelector(".js-gps-btn");
    if (knop) {
        knop.addEventListener("click", function() {
            socket.emit("F2B_get_GPS_data")
        });
    }

    knop = document.querySelector(".js-arrival");
    if (knop) {
        knop.addEventListener("click", function() {
            socket.emit("F2B_update_endtime")
        });
    }

    let toggleTrigger = document.querySelectorAll(".js-toggle-nav");
    for (let i = 0; i < toggleTrigger.length; i++) {
        toggleTrigger[i].addEventListener("click", function() {
            document.querySelector("body").classList.toggle("has-mobile-nav");
        })
    }
};


const listenToSocket = function() {
    socket.on("connected", function() {
        console.log("verbonden met socket webserver");
    });

    socket.on("B2F_redirect_index", function() {
        window.location.replace("http://192.168.0.100/");
    });

    socket.on("B2F_return_orders", function(data) {
        //console.log(data);
        document.querySelector(".js-orderZone").innerHTML = data;
        loadMap();
        listenToUI();
        socket.emit("F2B_get_route")
    });

    socket.on("B2F_return_route", function(data) {
        console.log(data);
        for (i of data) {
            latitude = i["latitude"];
            longitude = i["longitude"];
            console.log(i);
            var marker = L.marker([latitude, longitude]).addTo(mymap);
        }
    });

    //in stap 2
    socket.on("B2F_return_accel_data", function(jsonObject) {
        console.log(jsonObject);
        /* document.querySelector(".js-accel").innerHTML = jsonObject.accel_data;
        document.querySelector(".js-shock").innerHTML = (jsonObject.shocks + " shocken"); */
    });

    socket.on("B2F_return_GPS_data", function(jsonObject) {
        console.log(jsonObject);
        /* console.log(jsonObject.Latitude);
        console.log(jsonObject.Longitude);
        console.log(jsonObject.Speed);

        latitude = jsonObject.Latitude
        longitude = jsonObject.Longitude
        speed = (jsonObject.Speed * 1.852)
        speed = Number((speed).toFixed(6));

        document.querySelector(".js-lat").innerHTML = (latitude + " graden");
        document.querySelector(".js-long").innerHTML = (longitude + " graden");
        document.querySelector(".js-speed").innerHTML = (speed + " km/h"); */

        mymap.eachLayer(function(layer) {
            mymap.removeLayer(layer);
        });
        LoadTitleLayer();
        mymap.setView([latitude, longitude], 17);
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

const loadMap = function() {
    //document.querySelector(".js-shock").innerHTML = "0 shocken";
    mymap = L.map('mapid').setView([50.84673, 4.35247], 12);
    LoadTitleLayer();
    socket.emit("F2B_setup_GPS");
};

const createOrder = function() {
    submitform = getUrlVars(window.location.href);
    console.log(submitform);
    socket.emit("F2B_create_order", submitform);
};

function getUrlVars(url) {
    var hash;
    var myJson = {};
    var hashes = url.slice(url.indexOf('?') + 1).split('&');
    for (var i = 0; i < hashes.length; i++) {
        hash = hashes[i].split('=');
        myJson[hash[0]] = hash[1];
    }
    return myJson;
}

document.addEventListener("DOMContentLoaded", function() {
    console.info("DOM geladen");
    html_mapidHolder = document.querySelectorAll(".js-mapid");
    html_ordersHolder = document.querySelector(".js-orders");

    if (html_mapidHolder) {
        socket.emit("F2B_get_last_order");
    }

    if (html_mapidHolder) {
        loadMap();
    }

    if ((window.location.href).includes("?")) {
        console.log("submit found");
        createOrder();
    }

    listenToUI();
    listenToSocket();
});