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

i2c = busio.I2C(board.SCL, board.SDA)
mpu = adafruit_mpu6050.MPU6050(i2c)

# import adafruit_gps

# uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)
# gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
# gps.send_command(b"PMTK220,1000")


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
    adafruitGPS_data = "missing"
    socketio.emit('BF2_return_GPS_data', adafruitGPS_data)


if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')
