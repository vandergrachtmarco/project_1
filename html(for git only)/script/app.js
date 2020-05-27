const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

const listenToUI = function() {
    knop = document.querySelector(".js-data-btn");
    knop.addEventListener("click", function() {
        socket.emit("F2B_get_accel_data")
    });
};

const listenToSocket = function() {
    socket.on("connected", function() {
        console.log("verbonden met socket webserver");
    });

    //in stap 2
    socket.on("B2F_return_accel_data", function(jsonObject){
        console.log(jsonObject);
        document.querySelector(".js-accel").innerHTML = "data.accel_data";
        document.querySelector(".js-accel").innerHTML = jsonObject.accel_data;
        document.querySelector(".js-shock").innerHTML = (jsonObject.shocks + " shocken");
    });
};

document.addEventListener("DOMContentLoaded", function() {
    console.info("DOM geladen");
    document.querySelector(".js-shock").innerHTML = "0 shocken";
    listenToUI();
    listenToSocket();
});