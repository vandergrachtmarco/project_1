const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

var mymap

const listenToUI = function() {
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

    socket.on("B2F_return_products", function(data) {
        //console.log(data);
        document.querySelector(".js-productZone").innerHTML = data;
    });
};

document.addEventListener("DOMContentLoaded", function() {
    console.info("DOM geladen");

    socket.emit("F2B_get_products");
    socket.emit("F2B_show_IP");
    listenToUI();
    listenToSocket();
});