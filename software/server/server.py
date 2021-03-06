#!/usr/bin/env python

import sys
from flask import Flask, request, render_template
from werkzeug.exceptions import InternalServerError, BadRequest
from chandelier import Chandelier, BROADCAST
import function as src
import generator as g
import filter as f
import random as r
import common
from time import sleep, time
from color import Color
from pattern import pattern_set
from threading import Thread, Lock

STATIC_PATH = "/static"
STATIC_FOLDER = "static"
TEMPLATE_FOLDER = "template"

NORMAL_SPEED = 1000
MAX_SPEED = 3000
MIN_SPEED = 100
SPEED_STEPS = 400

MAX_BRIGHTNESS = 100
MIN_BRIGHTNESS = 10
BRIGHTNESS_STEPS =20 

TRANSITION_STEPS = 500

HOLD_DURATION = 30
MAX_DURATION = 120

# main chandelier object
ch = None
pm = None
speed = NORMAL_SPEED
brightness = MAX_BRIGHTNESS

class PatternMaster(Thread):
    def __init__(self, chandelier):
        Thread.__init__(self)
        self.ch = chandelier
        self.exit = False
        self.time_left = 0
        self.lock = Lock()
        self.pause = False

    def set_pause(self, p):
        self.pause = p

    def is_paused(self):
        return self.pause

    def gtfo(self):
        self.exit = True

    def hold(self):
        print "hold"
        self.lock.acquire()
        self.time_left = min(self.time_left + HOLD_DURATION, MAX_DURATION)
        self.lock.release()

    def skip(self):
        print "skip"
        self.lock.acquire()
        self.time_left = 0
        self.lock.release()

    def run(self):
        prev_delay = 0 
        print "pattern master starting"
        while not self.exit:
            for pat, delay, name in pattern_set:
                print name, delay
                if self.exit:
                    break

                self.ch.send_pattern(BROADCAST, pat)
                self.ch.next_pattern(BROADCAST, TRANSITION_STEPS)
   
                self.lock.acquire()
                self.time_left = prev_delay
                self.lock.release()
                while True:
                    sleep(1)
                    self.lock.acquire()
                    self.time_left -= 1
                    tl = self.time_left
                    self.lock.release()
                    if tl <= 0:
                        break

                    if self.pause:
                        while self.pause:
                            sleep(1)

                    if self.exit:
                        break

                prev_delay = delay

        print "pattern master exiting"

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
    pm.skip()
    return "ok"

@app.route('/ctrl/hold')
def hold():
    pm.hold()
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

@app.route('/resume')
def resume():
    global pm, ch
    pm.set_pause(False)
    return ""

@app.route('/run', methods=["POST"])
def run():
    global pm, ch
    prog = request.data
    try:
        data = eval(prog)
    except Exception as e:
        print e
        return e

    if pm and not pm.is_paused():
        pm.set_pause(True)
        sleep(1)

    ch.send_pattern(BROADCAST, data)
    ch.next_pattern(BROADCAST, TRANSITION_STEPS)
    return ":-)"

# global variables that need to be moved to a UWSI block
speed = NORMAL_SPEED

DELAY = .02

device = "/dev/ttyAMA0"

r.seed()

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

for p in range(1, 105):
    ch.set_position(p, r.random(), r.random(), 0)

ch.send_pattern(BROADCAST, pattern_set[0][0])
ch.next_pattern(BROADCAST, 0)

pm = PatternMaster(ch)
if __name__ == '__main__':
    pm.start()
    app.run(host='0.0.0.0', port=8080)
