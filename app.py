# pylint: skip-file
from repositories.DataRepository import DataRepository
from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS

import time
import threading
import board
import busio

import adafruit_mpu6050
import adafruit_gps
import serial

i2c = busio.I2C(board.SCL, board.SDA)
#mpu = adafruit_mpu6050.MPU6050(i2c)


gps = 0

# Code voor led
from helpers.klasseknop import Button
from RPi import GPIO

led1 = 21
knop1 = Button(20)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(led1, GPIO.OUT)


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

    adafruitGPS_data = {'Latitude': longitudewp, 'Longitude': latitudewp, 'Speed': speedwp}
    socketio.emit('B2F_return_GPS_data', adafruitGPS_data)


@socketio.on('F2B_setup_GPS')
def setup_GPS():
    print("setting up GPS")
    uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=10)
    gps = adafruit_gps.GPS(uart, debug=False)
    gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
    gps.send_command(b'PMTK220,1000')


if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')
