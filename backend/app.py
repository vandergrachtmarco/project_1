# pylint: skip-file
from repositories.DataRepository import DataRepository
from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS

import time
import threading
import board
import busio

from RPLCD.i2c import CharLCD
import socket
import adafruit_mpu6050
import adafruit_gps
import serial

i2c = busio.I2C(board.SCL, board.SDA)
# mpu = adafruit_mpu6050.MPU6050(i2c)


gps = 0

# Code voor led
from helpers.classbutton import Button
from RPi import GPIO

pinkers = 21
servo_pin = 18
knop1 = Button(25)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(pinkers, GPIO.OUT)
GPIO.setup(servo_pin, GPIO.OUT)

pwm_servo = GPIO.PWM(servo_pin, 50)
pwm_servo.start(5)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Hier mag je om het even wat schrijven, zolang het maar geheim blijft en een string is'

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)


# API ENDPOINTS
@app.route('/')
def hallo():
    return "Server is running, er zijn momenteel geen API endpoints beschikbaar."


# SOCKET IO
@socketio.on('connect')
def initial_connection():
    print('A new client connect')
    # # Send to the client!
    uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=10)
    gps = adafruit_gps.GPS(uart, debug=False)
    gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
    gps.send_command(b'PMTK220,1000')


@socketio.on('F2B_get_accel_data')
def get_accel_data():
    accelerometer_data = ("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2" % (mpu.acceleration))
    print(mpu.acceleration[0])

    shocksense = mpu.acceleration[0]
    amounts = DataRepository.read_aantal_shocken()
    amount = (amounts[0]).get('aantal_shocken')
    print(amount)
    if (shocksense < 6) | (shocksense > 14):
        amount += 1
        res = DataRepository.update_aantal_shocken(amount)
        print("shocks raised")
    else:
        print("shocks not raised")

    print(accelerometer_data)
    # print("Gyro X:%.2f, Y: %.2f, Z: %.2f degrees/s" % (mpu.gyro))
    # print("Temperature: %.2f C" % mpu.temperature)
    socketio.emit('B2F_return_accel_data', {'accel_data': accelerometer_data, 'shocks': amount})


@socketio.on('F2B_get_GPS_data')
def get_GPS_data():
    uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=10)
    gps = adafruit_gps.GPS(uart, debug=False)
    gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
    gps.send_command(b'PMTK220,1000')

    gps.update()

    while not gps.has_fix:
        print(gps.nmea_sentence)
        print('Waiting for fix...')
        gps.update()
        time.sleep(1)
        continue

    # print('=' * 40)  # Print a separator line.
    print('Latitude: {0:.6f} degrees'.format(gps.latitude))
    print('Longitude: {0:.6f} degrees'.format(gps.longitude))
    print("Speed: " + str(gps.speed_knots) + "knots")

    idwp = (((DataRepository.read_waypoints_maxid())['maxid']) + 1)
    longitudewp = float("{:.4f}".format(gps.longitude))
    latitudewp = float("{:.5f}".format(gps.latitude))
    speedwp = gps.speed_knots

    DataRepository.insert_waypoint(idwp, longitudewp, latitudewp, speedwp)

    adafruitGPS_data = {'Latitude': latitudewp, 'Longitude': longitudewp, 'Speed': speedwp}
    socketio.emit('B2F_return_GPS_data', adafruitGPS_data)


@socketio.on('F2B_setup_GPS')
def setup_GPS():
    print("setting up GPS")
    uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=10)
    gps = adafruit_gps.GPS(uart, debug=False)
    gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
    gps.send_command(b'PMTK220,1000')


@socketio.on('F2B_get_last_order')
def get_orders():
    print("getting last order")
    data = DataRepository.read_order_by_id((DataRepository.read_order_maxid())["maxid"])
    htmlholder = ''

    idorder = data["idorder"]
    ordertime = data["ordertime"]
    starttime = data["deliverystarttime"]
    endtime = data["deliveryendtime"]
    shocken = (DataRepository.read_aantal_shocken_by_idorder(idorder))["aantal_shocken"]
    price = DataRepository.read_order_cost_by_id(idorder)
    if price:
        price = price["price"]
    else:
        price = "0"

    htmlholder = f'<div class="column1" id="{idorder}">'
    htmlholder += f'<h3>ID:00{idorder}</h3>'
    # htmlholder += f'<div class="o-container mapholder{idorder}" id="{idorder}">'
    htmlholder += f'<div class="o-container mapholder{idorder}" id="{idorder}">'
    htmlholder += f'<div id="mapid" class="js-mapid"></div></div>'
    if starttime:
        if endtime:
            htmlholder += f'<div class="columnText">aangekomen: {endtime}</div>'
            if shocken is None:
                htmlholder += f'<div class="columnText">aantal shocken: 0</div>'
            else:
                htmlholder += f'<div class="columnText">aantal shocken: {shocken}</div>'
            htmlholder += f'<div class="columnText">duurtijd: {endtime - ordertime}</div>'
            htmlholder += f'<div class="columnText">AANGEKOMEN </div>'
            htmlholder += f'<div class="columnLink">totaal: €{price}<span class="order">| Details</span> </div></div>'
        else:
            htmlholder += f'<div class="columnText">vertroken: {starttime}</div>'
            htmlholder += f'<div class="columnText">ONDERWEG</div>'
            htmlholder += f'<div class="columnLink">totaal: €{price}<span class="order js-arrival">| Aankomst bevestigen</span> </div></div>'
    else:
        htmlholder += f'<div class="columnText">besteld: {ordertime}</div>'
        htmlholder += f'<div class="columnText">IN DE OVEN</div>'
        htmlholder += f'<div class="columnLink">totaal: €{price}<span class="order">| Geduld aub</span> </div></div>'

    update_flag_position()
    socketio.emit('B2F_return_orders', htmlholder)


@socketio.on('F2B_create_order')
def create_order(data):
    filtered = {k: v for k, v in data.items() if v != ''}

    idorder = ((DataRepository.read_order_maxid())["maxid"]) + 1
    adress = str(filtered["street"]) + " " + str(filtered["number"])
    datetime = time.strftime("%Y-%m-%d %H:%M:%S")

    DataRepository.create_order(idorder, adress, datetime)

    filtered = {k: v for k, v in filtered.items() if k != 'street'}
    filtered = {k: v for k, v in filtered.items() if k != 'number'}

    for k, v in filtered.items():
        category = (DataRepository.get_category_by_idproduct(k))['idcategory']
        DataRepository.create_order_item(idorder, k, category, v)

    update_flag_position()
    socketio.emit('B2F_redirect_index')


@socketio.on('F2B_get_products')
def get_products():
    datapack = DataRepository.read_products()
    htmlholder = '<div><div class="u-1-of-2"><label for="street">straatnaam:</label><div><input type="text" id="street" name="street"></div></div><div class="u-1-of-2"><label for="number">huisnummer:</label><div><input type="text" id="number" name="number"></div></div></div>'

    for data in datapack:
        idproduct = data["idproduct"]
        name = data["name"]
        description = data["description"]
        category = data["category"]
        price = data["price"]
        instock = data["instock"]

        htmlholder += '<div class="column1 columnproduct">'
        htmlholder += f'<h3>{name}</h3>'
        htmlholder += '<!-- <img src="images/product.png" alt="" /> -->'
        htmlholder += '<svg class="c-picture" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 311 311">'
        htmlholder += '<title>Placeholder logo</title>'
        htmlholder += '<rect width="279px" height="300px" style="fill:rgb(128,128,128);" /></svg>'
        if description != "null":
            htmlholder += f'<div>{description}</div>'
        htmlholder += f'<div>{category}</div>'
        htmlholder += f'<div><input type="number" id="{idproduct}" name="{idproduct}" min="1" max="100"> Stuk</div>'
        if instock == 1:
            htmlholder += f'<div class="columnLink">€{price}<span class="order">| <a href="#"><input type="submit" value="Submit"></a></span></div></div>'
        else:
            htmlholder += f'<div class="columnLink">€{price}<span class="order">|Out of stock</span></div></>'

    socketio.emit('B2F_return_products', htmlholder)


@socketio.on('F2B_get_route')
def get_route():
    route = DataRepository.read_waypoints_by_idorder((DataRepository.read_order_maxid())["maxid"])
    socketio.emit('B2F_return_route', route)


def show_IP():
    lcd = CharLCD('PCF8574', 0x27)
    datetime = time.strftime("%H:%M")
    lcd.write_string('tijd:'+str(datetime)+'\r\nip:'+str(get_ip_address()))


@socketio.on('F2B_update_endtime')
def update_endtime():
    print("arrival btn pressed")
    datetime = time.strftime("%Y-%m-%d %H:%M:%S")
    orderid = (DataRepository.read_order_maxid())["maxid"]
    print(datetime)
    DataRepository.update_order_end(orderid, datetime)
    get_orders()


def update_starttime():
    print("button pressed")
    datetime = time.strftime("%Y-%m-%d %H:%M")
    orderid = (DataRepository.read_order_maxid())["maxid"]
    print(datetime)
    DataRepository.update_order_start(orderid, datetime)
    update_flag_position()
    get_orders()


def update_flag_position():
    data = DataRepository.read_order_by_id((DataRepository.read_order_maxid())["maxid"])
    starttime = data["deliverystarttime"]
    endtime = data["deliveryendtime"]

    if starttime:
        pwm_servo.ChangeDutyCycle(5)
    else:
        pwm_servo.ChangeDutyCycle(10)


def get_ip_address():
    ip_address = ''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address


def pinker_loop():
    print("starting indicator loop")
    while True:
        GPIO.output(pinkers, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(pinkers, GPIO.LOW)
        time.sleep(1)


def gps_loop():
    uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=10)
    gps = adafruit_gps.GPS(uart, debug=False)
    gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
    gps.send_command(b'PMTK220,1000')

    while True:
        gps.update()

        while not gps.has_fix:
            print('Waiting for fix...')
            gps.update()
            time.sleep(1)
            continue

        idwp = (((DataRepository.read_waypoints_maxid())['maxid']) + 1)
        idorder = (DataRepository.read_order_maxid())["maxid"]
        longitudewp = float("{:.4f}".format(gps.longitude))
        latitudewp = float("{:.5f}".format(gps.latitude))
        speedwp = gps.speed_knots

        DataRepository.insert_waypoint(idwp, longitudewp, latitudewp, speedwp)

        DataRepository.create_order_route(idorder, idwp)

        show_IP()
        time.sleep(60)


def mpu_loop():
        accelerometer_data = ("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2" % (mpu.acceleration))
        print(mpu.acceleration[0])

        shocksense = mpu.acceleration[0]
        idorder = (DataRepository.read_order_maxid())["maxid"]
        amounts = DataRepository.read_aantal_shocken_by_idorder(idorder)
        amount = (amounts[0]).get('aantal_shocken')
        print(amount)
        if (shocksense < 6) | (shocksense > 14):
            amount += 1
            DataRepository.update_aantal_shocken(idorder, amount)
            print("shocks raised")
        else:
            print("shocks not raised")

        time.sleep(1)


knop1.on_press(update_starttime)

if __name__ == '__main__':
    show_IP()
    pinker_proces = threading.Thread(target=pinker_loop)
    gps_proces = threading.Thread(target=gps_loop)
    mpu_proces = threading.Thread(target=mpu_loop)
    #pinker_proces.start()
    #gps_proces.start()
    #mpu_proces.start()
    socketio.run(app, debug=False, host='0.0.0.0')
