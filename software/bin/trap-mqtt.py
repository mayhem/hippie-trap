#!/usr/bin/python

import os
import sys
import math
import socket
import paho.mqtt.client as mqtt
import json
from time import sleep

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

CLIENT_ID = socket.gethostname()
DISCOVER_TOPIC = "homeassistant/light/hippietrap/config"
COMMAND_TOPIC = "home/hippietrap/set"
STATE_TOPIC = "home/hippietrap/state"
BRIGHTNESS_TOPIC = "home/hippietrap/brightness"
BRIGHTNESS_STATE_TOPIC = "home/hippietrap/brightness_state"
RGB_COLOR_TOPIC = "home/hippietrap/rgb"
EFFECT_TOPIC = "home/hippietrap/effect"
REDISCOVER_TOPIC = "rediscover"

class HippieTrapMQTT(HippieTrap):

    def __init__(self):
        HippieTrap.__init__(self)
        self.state = False
        self.patterns = []
        self.current_pattern = None

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
            self.clear(ALL)

        if not new_pattern:
            return


        self.current_pattern = new_pattern(self)
        self.current_pattern.start()


    @staticmethod
    def on_message(mqttc, user_data, msg):
        try:
            mqttc.__ht._handle_message(mqttc, msg)
        except Exception, err:
            print "exception!", err
            print traceback.format_exc()


    def _handle_message(self, mqttc, msg):
        payload = msg.payload # str(msg.payload, 'utf-8')
        if msg.topic == COMMAND_TOPIC:
            if msg.payload.lower() == b"on":
                if not self.state:
                    self.state = True
                    self.power_off()
                    sleep(.1)
                    self.power_on()
                    sleep(2)
                mqttc.publish(STATE_TOPIC, "ON")
                return

            if msg.payload.lower() == b"off":
                if self.state:
                    self.state = False
                    self.power_off()
                mqttc.publish(STATE_TOPIC, "OFF")
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
        
        if msg.topic == RGB_COLOR_TOPIC:
            r,g,b = payload.split(",")
            color = (int(r),int(g),int(b))
            self.current_pattern.set_color(color)
            return
           
        if msg.topic == REDISCOVER_TOPIC:
            self.send_discover_msg()
            return


    def send_discover_msg(self):

        effect_name_list = []
        for pattern in self.patterns:
            effect_name_list.append(pattern.name)

        self.mqttc.publish(DISCOVER_TOPIC, json.dumps(
            {
                "name": "hippie trap",
                "command_topic": COMMAND_TOPIC, 
                "state_topic": STATE_TOPIC, 
                "device_class": "light",
                "assumed_state": "true",
                "rgb_color" : "true",
                "rgb_command_topic" : RGB_COLOR_TOPIC,
                "effect" : "true",
                "effect_command_topic": EFFECT_TOPIC,
                "effect_list": effect_name_list,
                "brightness" : "true",
                "brightness_scale" : "100",
                "brightness_command_topic": BRIGHTNESS_TOPIC,
#                "brightness_state_topic": BRIGHTNESS_STATE_TOPIC,
            }))


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
        self.mqttc.subscribe(RGB_COLOR_TOPIC)
        self.mqttc.subscribe(REDISCOVER_TOPIC)
        self.send_discover_msg()


if __name__ == "__main__":
    with HippieTrapMQTT() as ht:
        ht.add_pattern(TexturePattern)
        ht.add_pattern(SweepTwoColorShiftPattern)
        ht.add_pattern(SweepOneColorPerRingPattern)
        ht.add_pattern(SwappiesPattern)
        ht.add_pattern(RandomColorsPattern)
        ht.add_pattern(EachBottleOneRainbowPattern)
        ht.add_pattern(FireIceCirclesPattern)
        ht.add_pattern(SolidPattern)
        ht.add_pattern(RainbowPattern)
        ht.setup()
        try:
            while True:
                sleep(100)
        except KeyboardInterrupt:
            ht.set_pattern("")
            ht.clear(ALL)
            ht.mqttc.publish(DISCOVER_TOPIC, "")
            ht.mqttc.disconnect()
            ht.mqttc.loop_stop()
