#!/usr/bin/env python3

import os
import sys
import math
import socket
import random
import paho.mqtt.client as mqtt
import json
import copy
from time import sleep, time

from hippietrap.hippietrap import HippieTrap, ALL
from hippietrap.patterns.rainbow import RainbowPattern
from hippietrap.patterns.solid import SolidPattern
from hippietrap.patterns.fire_ice_circles import FireIceCirclesPattern
from hippietrap.patterns.each_bottle_one_rainbow import EachBottleOneRainbowPattern
from hippietrap.patterns.random_colors import RandomColorsPattern
from hippietrap.patterns.swappies import SwappiesPattern
from hippietrap.patterns.sweep_one_color_per_ring import SweepOneColorPerRingPattern
from hippietrap.patterns.sweep_two_color_shift import SweepTwoColorShiftPattern
from hippietrap.patterns.texture import TexturePattern
from hippietrap.patterns.sweep_gradient import SweepGradientPattern
from hippietrap.patterns.spread_outward import SpreadOutwardPattern

CLIENT_ID = socket.gethostname()
COMMAND_TOPIC = "hippietrap/command"
STATE_TOPIC = "hippietrap/state"
BRIGHTNESS_TOPIC = "hippietrap/brightness"
BRIGHTNESS_STATE_TOPIC = "hippietrap/brightness_state"
COLOR_TOPIC = "hippietrap/color"
COLOR_STATE_TOPIC = "hippietrap/color_state"
EFFECT_TOPIC = "hippietrap/effect"

class HippieTrapMQTT(HippieTrap):

    UPDATE_INTERVAL = 10

    def __init__(self):
        HippieTrap.__init__(self)
        self.state = False
        self.patterns = []
        self.current_pattern = None
        self.random_patterns = None
        self.next_update = 0


    @property
    def enabled(self):
        return self.state


    def enable(self, enabled):
        if not self.state and enabled:
            self.state = True
            print("turn on power")
            self.power_on()
            if self.current_pattern:
                print("start pattern")
                self.current_pattern.enable(True)

        if self.state and not enabled:
            self.state = False
            print("turn off power")
            if self.current_pattern:
                self.current_pattern.enable(False)
                self.set_pattern("")
            self.power_off()


    def set_random_pattern(self):
        if not self.random_patterns:
            self.random_patterns = copy.deepcopy(self.patterns)

        index = random.randint(0, len(self.random_patterns) - 1)
        self.set_pattern(ht.random_patterns[index].name)
        del self.random_patterns[index]


    def add_pattern(self, pattern):
        self.patterns.append(pattern)


    def set_pattern(self, pattern_name):
        new_pattern = None
        for pattern in self.patterns:
            if pattern.name == pattern_name:
                new_pattern = pattern
                break

        if self.current_pattern:
            self.current_pattern.stop()
            self.current_pattern.join()

        if not new_pattern:
            self.next_update = 0
            self.current_pattern = None
            return

        self.current_pattern = new_pattern(self)
        print("start pattern '%s'" % self.current_pattern.name)
        self.current_pattern.start()
        self.current_pattern.enable(True)
        self.next_update = time() + self.UPDATE_INTERVAL


    @staticmethod
    def on_message(mqttc, user_data, msg):
        try:
            mqttc.__ht._handle_message(mqttc, msg)
        except Exception as err:
            print("exception!", err)
            print(traceback.print_strack())


    def _handle_message(self, mqttc, msg):
        payload = msg.payload # str(msg.payload, 'utf-8')
        if msg.topic == COMMAND_TOPIC:
            if msg.payload.lower() == b"1":
                self.enable(True)
                self.set_random_pattern()
                mqttc.publish(STATE_TOPIC, "1")
                return

            if msg.payload.lower() == b"0":
                self.enable(False)
                self.set_pattern("")
                mqttc.publish(STATE_TOPIC, "0")
                return
            return

        if msg.topic == BRIGHTNESS_TOPIC:
            try:
                self.set_brightness(ALL, int(msg.payload))
            except ValueError:
                pass
            return
  
        if msg.topic == EFFECT_TOPIC:
            try:
                self.set_pattern(msg.payload)
            except ValueError:
                pass
            return
        
        if msg.topic == COLOR_TOPIC:
            r,g,b = payload.split(",")
            color = (int(r),int(g),int(b))
            self.current_pattern.set_color(color)
            return
           

    def setup(self):

        self.begin()

        self.mqttc = mqtt.Client(CLIENT_ID)
        self.mqttc.on_message = HippieTrapMQTT.on_message
        self.mqttc.connect("10.1.1.2", 1883, 60)
        self.mqttc.loop_start()
        self.mqttc.__ht = self

        self.mqttc.subscribe(COMMAND_TOPIC)
        self.mqttc.subscribe(BRIGHTNESS_TOPIC)
        self.mqttc.subscribe(EFFECT_TOPIC)
        self.mqttc.subscribe(COLOR_TOPIC)
        self.mqttc.publish(STATE_TOPIC, "%d" % self.state)

    def loop(self):
        if self.next_update and time() > self.next_update:
            self.set_random_pattern()

        sleep(.1)


if __name__ == "__main__":
    with HippieTrapMQTT() as ht:
        ht.add_pattern(SpreadOutwardPattern)
        ht.add_pattern(SweepGradientPattern)
        ht.add_pattern(SweepTwoColorShiftPattern)
        ht.add_pattern(SweepOneColorPerRingPattern)
        ht.add_pattern(SwappiesPattern)
        ht.add_pattern(RandomColorsPattern)
        ht.add_pattern(EachBottleOneRainbowPattern)
        ht.add_pattern(FireIceCirclesPattern)
        ht.add_pattern(RainbowPattern)
#        ht.add_pattern(TexturePattern)
        ht.setup()
        ht.set_brightness(ALL,50)
        print("ready!")
        try:
            while True:
                ht.loop()
        except KeyboardInterrupt:
            print("break! shutting down")
            ht.set_pattern("")
            ht.clear(ALL)
            ht.power_off()
            ht.mqttc.publish(STATE_TOPIC, "X")
            ht.mqttc.disconnect()
            ht.mqttc.loop_stop()
