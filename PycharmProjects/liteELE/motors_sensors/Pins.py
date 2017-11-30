# By Mattia Melli

import math
import subprocess
import time

import Adafruit_MPR121.MPR121 as MPR121
import RPi.GPIO as GPIO
import smbus
from motors_sensors import MFRC522
from neopixel import *

# BCM to WiringPi pin numbers
LED = 24  # LED pin

LED_RGB = 18  # GPIO pin connected to the pixels

S4 = 22  # Servo pin
S3 = 27  # Servo pin
S2 = 17  # Servo pin
S1 = 0o4  # Servo pin

Motor1A = 19
Motor1B = 13
Motor1E = 26
Motor2A = 20
Motor2B = 21
Motor2E = 16

# Create MPR121 instance. Capacitive sensor
cap = MPR121.MPR121()

# LED strip configuration:
LED_COUNT = 10  # Number of LED pixels
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 5  # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_RGB, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
strip.begin()

# Create an object of the class MFRC522. RFID reader
MIFAREReader = MFRC522.MFRC522()

# Accelerometer
bus = smbus.SMBus(1)
power_mgmt_1 = 0x6b
address = 0x68
try:
    bus.write_byte_data(address, power_mgmt_1, 0)
except:
    pass

# Inizialize the start position os Servo Motors
pos_servo_1 = 0
pos_servo_2 = 0
pos_servo_3 = 0
pos_servo_4 = 0


def Init():
    GPIO.setwarnings(False)  # suppress GPIO used message
    # GPIO.setmode(GPIO.BCM)	#use BCM pin numbers, gia impostato nella libreria MFRC522
    GPIO.setup(LED, GPIO.OUT)
    GPIO.setup(S1, GPIO.OUT)
    GPIO.setup(S2, GPIO.OUT)
    GPIO.setup(S3, GPIO.OUT)
    GPIO.setup(S4, GPIO.OUT)
    GPIO.setup(Motor1A, GPIO.OUT)
    GPIO.setup(Motor1B, GPIO.OUT)
    GPIO.setup(Motor1E, GPIO.OUT)
    GPIO.setup(Motor2A, GPIO.OUT)
    GPIO.setup(Motor2B, GPIO.OUT)
    GPIO.setup(Motor2E, GPIO.OUT)

    # inizialize MPR121
    try:
        cap.begin()
    except:
        pass

    # inizialize Servo
    InitServo()


def InitServo():
    global pos_servo_1
    global pos_servo_2
    global pos_servo_3
    global pos_servo_4
    # the last stimated Servo Motor position: 90
    ServoPos(S1, 90, pos_servo_1)
    ServoPos(S2, 90, pos_servo_2)
    ServoPos(S3, 90, pos_servo_3)
    ServoPos(S4, 90, pos_servo_4)


def LEDon():
    GPIO.output(LED, GPIO.HIGH)


def LEDoff():
    GPIO.output(LED, GPIO.LOW)


def SetLED(state):
    if state:
        LEDon()
    else:
        LEDoff()


def Servo(s, position):
    global pos_servo_1
    global pos_servo_2
    global pos_servo_3
    global pos_servo_4

    if s == "1":
        pos_servo = ServoPos(S1, pos_servo_1, position)
        pos_servo_1 = pos_servo
    elif s == "2":
        pos_servo = ServoPos(S2, pos_servo_2, position)
        pos_servo_2 = pos_servo
    elif s == "3":
        pos_servo = ServoPos(S3, pos_servo_3, position)
        pos_servo_3 = pos_servo
    elif s == "4":
        pos_servo = ServoPos(S4, pos_servo_4, position)
        pos_servo_4 = pos_servo


# 0 degree -> 2.5    180 degree -> 12.5
def ServoPos(s, pos_servo, position):
    p = GPIO.PWM(s, 50)

    if pos_servo < int(position):
        p.start(pos_servo / 18 + 2.5)
        for i in range(pos_servo, int(position) + 1):
            pos = float(i) / 18 + 2.5
            p.ChangeDutyCycle(pos)
            time.sleep(0.005)
        pos_servo_ret = int(position)
    else:
        p.start(pos_servo / 18 + 2.5)
        for i in range(pos_servo, int(position) - 1, -1):
            pos = float(i) / 18 + 2.5
            p.ChangeDutyCycle(pos)
            time.sleep(0.005)
        pos_servo_ret = int(position)

    p.stop()

    return pos_servo_ret


def ledRGB(r, g, b, action):
    if action == "on":
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(int(g), int(r), int(b)))
        strip.show()
    else:
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()


def dcMotor(m, action):
    if m == "1":
        # forwards
        if action == "on-f":
            GPIO.output(Motor1A, GPIO.HIGH)
            GPIO.output(Motor1B, GPIO.LOW)
            GPIO.output(Motor1E, GPIO.HIGH)
        # backwards
        if action == "on-b":
            GPIO.output(Motor1A, GPIO.LOW)
            GPIO.output(Motor1B, GPIO.HIGH)
            GPIO.output(Motor1E, GPIO.HIGH)
        if action == "off":
            GPIO.output(Motor1E, GPIO.LOW)

    if m == "2":
        # forwards
        if action == "on-f":
            GPIO.output(Motor2A, GPIO.HIGH)
            GPIO.output(Motor2B, GPIO.LOW)
            GPIO.output(Motor2E, GPIO.HIGH)
        # backwards
        if action == "on-b":
            GPIO.output(Motor2A, GPIO.LOW)
            GPIO.output(Motor2B, GPIO.HIGH)
            GPIO.output(Motor2E, GPIO.HIGH)
        if action == "off":
            GPIO.output(Motor2E, GPIO.LOW)


def ReadCapacitive():
    current_touched = cap.touched()
    if cap.is_touched(0):
        return ("0")
    if cap.is_touched(1):
        return ("1")
    if cap.is_touched(2):
        return ("2")
    if cap.is_touched(3):
        return ("3")
    return ("null")


def ReadRfid():
    cardUID = "null"
    # Scan for cards
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # Get the UID of the card
    (status, uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:
        cardUID = str(uid[0]) + str(uid[1]) + str(uid[2]) + str(uid[3])

    return (cardUID)


def connect(ssid, password):
    subprocess.check_call(['sudo', 'bash', '/home/pi/ele_v4/connect.sh', ssid, password])


# -----------------------------------------------------------------Accelerometer-----------------------------------------------------------------
def read_word(reg):
    h = bus.read_byte_data(address, reg)
    l = bus.read_byte_data(address, reg + 1)
    value = (h << 8) + l
    return value


def read_word_2c(reg):
    val = read_word(reg)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val


def dist(a, b):
    return math.sqrt((a * a) + (b * b))


def get_y_rotation(x, y, z):
    radians = math.atan2(x, dist(y, z))
    return -math.degrees(radians)


def get_x_rotation(x, y, z):
    radians = math.atan2(y, dist(x, z))
    return math.degrees(radians)


def readAccelerometer():
    beschleunigung_xout = read_word_2c(0x3b)
    beschleunigung_yout = read_word_2c(0x3d)
    beschleunigung_zout = read_word_2c(0x3f)

    beschleunigung_xout_skaliert = beschleunigung_xout / 16384.0
    beschleunigung_yout_skaliert = beschleunigung_yout / 16384.0
    beschleunigung_zout_skaliert = beschleunigung_zout / 16384.0

    x_value = int(
        get_x_rotation(beschleunigung_xout_skaliert, beschleunigung_yout_skaliert, beschleunigung_zout_skaliert))
    y_value = int(
        get_y_rotation(beschleunigung_xout_skaliert, beschleunigung_yout_skaliert, beschleunigung_zout_skaliert))

    values = str(x_value) + "|" + str(y_value)

    return (values)
