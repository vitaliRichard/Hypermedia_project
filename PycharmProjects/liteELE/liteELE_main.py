from flask import Flask, request, jsonify
import motors_sensors.motors_manager as m_manager
from motors_sensors.motors_manager import Proboscis
import motors_sensors.Pins as Pins

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


# ------------------------------------------
# START Motors and Sensors (by Mattia Melli)

# Polling
@app.route("/_getVar")
def _getVar():
    # Read capacitive sensor
    try:
        pressed = Pins.ReadCapacitive()
    except:
        pressed = "null"

    # Read RFID
    try:
        rfid = Pins.ReadRfid()
    except:
        rfid = "null"

    # Read accelorometer
    try:
        accelorometer = Pins.readAccelerometer()
        accValue = accelorometer.split("|")
        accXValue = accValue[0]
        accYValue = accValue[1]

    except:
        accXValue = "null",
        accYValue = "null"

    return jsonify(press=pressed,
                   rfid=rfid,
                   accX=accXValue,
                   accY=accYValue)


# Status LED
@app.route("/_led")
def _led():
    # status -> on, off
    state = request.args.get('status')
    if state == "on":
        Pins.LEDon()
    else:
        Pins.LEDoff()
    return "ok"


# Servo Motor
@app.route("/_servo")
def _servo():
    # s -> servo number
    # position -> position in degrees
    s = request.args.get('s')
    position = request.args.get('position')
    Pins.Servo(s, position)
    return "ok"


# RGB LED
@app.route("/_ledRGB")
def _ledRGB():
    # r -> red
    # g -> green
    # b -> blue
    # action -> (on, off)
    r = request.args.get('r')
    g = request.args.get('g')
    b = request.args.get('b')
    action = request.args.get('action')
    Pins.ledRGB(r, g, b, action)
    return "ok"


# DC Motor
@app.route("/_dcMotor")
def _dcMotor():
    # m -> motor number
    # action -> (forwards rotation, backwards rotation, stop)
    m = request.args.get('m')
    action = request.args.get('action')
    Pins.dcMotor(m, action)
    return "ok"

# END Motors and Sensors (by Mattia Melli)
# ------------------------------------------


def start_web_server():
    Pins.Init()
    port = 80
    m_manager.start_movements_queue()
    app.run(host='0.0.0.0', port=port)


if __name__ == "__main__":
    start_web_server()