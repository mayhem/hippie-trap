#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Example program to send packets to the radio
#
# João Paulo Barraca <jpbarraca@gmail.com>
#

from nrf24 import NRF24
import time
from struct import pack

pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

radio = NRF24()
radio.begin(0, 0, 22 , 25) #Set CE and IRQ pins
radio.setRetries(15,15)
radio.setPayloadSize(3)
radio.setChannel(160)

radio.setDataRate(NRF24.BR_1MBPS)
radio.setPALevel(NRF24.RF_PWR_HIGH | NRF24.RF_PWR_LOW)

radio.openWritingPipe([ 0x45, 0, 0, 0, 0 ])
radio.printDetails()

while True:
    buf = pack("<BBB", 255, 0, 0);
    radio.write(buf)
    time.sleep(1)
    buf = pack("<BBB", 0, 0, 255);
    radio.write(buf)
    time.sleep(1)
