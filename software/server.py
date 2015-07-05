#!/usr/bin/env python
    
from chandelier import Chandelier, BROADCAST
import function
import generator
import filter
import random
import common
from time import sleep, time
from color import Color

from flask import Flask, request, render_template

STATIC_PATH = "/static"
STATIC_FOLDER = "static"
TEMPLATE_FOLDER = "template"

NORMAL_SPEED = 1000
MAX_SPEED = 3000
MIN_SPEED = 100
SPEED_STEPS = 100

MAX_BRIGHTNESS = 100
MIN_BRIGHTNESS = 10
BRIGHTNESS_STEPS = 5

# main chandelier object
ch = None
speed = NORMAL_SPEED
brightness = MAX_BRIGHTNESS

app = Flask(__name__,
        static_url_path = STATIC_PATH,
        static_folder = STATIC_FOLDER,
        template_folder = TEMPLATE_FOLDER)

def inc_speed():
    global speed
    if speed < MAX_SPEED:
        speed += SPEED_STEPS
        print "speed: %d" % speed
        ch.set_speed(BROADCAST, speed)

def dec_speed():
    global speed
    if speed > MIN_SPEED:
        speed -= SPEED_STEPS
        print "speed: %d" % speed
        ch.set_speed(BROADCAST, speed)

def inc_brightness():
    global brightness
    if brightness < MAX_BRIGHTNESS:
        brightness += BRIGHTNESS_STEPS
        print "brightness: %d" % brightness
        ch.set_brightness(BROADCAST, brightness)

def dec_brightness():
    global brightness
    if brightness > MIN_BRIGHTNESS:
        brightness -= BRIGHTNESS_STEPS
        print "brightness: %d" % brightness
        ch.set_brightness(BROADCAST, brightness)

@app.route('/')
def index():
    return render_template("index", title="Hue Chandelier")

@app.route('/ctrl/skip')
def skip():
    print "skip"
    # skip
    return "ok"

@app.route('/ctrl/hold')
def hold():
    print "hold"
    # hold
    return "ok"

@app.route('/ctrl/bdown')
def bdown():
    dec_brightness()
    return "ok"

@app.route('/ctrl/bup')
def bup():
    inc_brightness()
    return "ok"

@app.route('/ctrl/sup')
def sup():
    inc_speed()
    return "ok"

@app.route('/ctrl/sdown')
def sdown():
    dec_speed()
    return "ok"

@app.route('/run', methods=["POST"])
def run():
    print request.data
    return ""


# global variables that need to be moved to a UWSI block
speed = NORMAL_SPEED

DELAY = .02

device = "/dev/ttyAMA0"

random.seed()

#try:
#    import uwsgi
#    have_uwsgi = True
#except ImportError:
#    have_uwsgi = False

ch = Chandelier()
ch.open(device)
ch.off(BROADCAST)
ch.send_entropy()
ch.set_brightness(BROADCAST, 100)

app.ch = ch

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
