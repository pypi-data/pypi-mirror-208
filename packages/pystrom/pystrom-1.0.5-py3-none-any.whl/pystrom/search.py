# Rafael Urben, 2021
#
# https://github.com/rafaelurben/python-mystrom

import socket
import requests
from pystrom.device import MyStromDevice
from pystrom.utils import log

class MyStromSearch():
    UDP_IP = "0.0.0.0"
    UDP_PORT = 7979

    sock = socket.socket(socket.AF_INET,        # Internet
                         socket.SOCK_DGRAM)     # UDP
    sock.bind((UDP_IP, UDP_PORT))

    @classmethod
    def searchall(cls):
        log("Looking for devices...")

        ipsfound = []
        devicesfound = []

        try:
            while True:
                cls.sock.settimeout(5.0)
                data, addr = cls.sock.recvfrom(1024)        # buffer size is 1024 bytes

                if not addr[0] in ipsfound:
                    x = MyStromDevice.from_announcement(data, addr[0])
                    log(x)

                    ipsfound.append(addr[0])
                    devicesfound.append(x)
                else:
                    break
        except socket.timeout:
            pass

        log(str(len(devicesfound))+" devices found!")
        return devicesfound

    @classmethod
    def searchlive(cls):
        log("Looking for devices... (Press Ctrl+C to exit!)")

        try:
            while True:
                try:
                    cls.sock.settimeout(5.0)
                    data, addr = cls.sock.recvfrom(1024)        # buffer size is 1024 bytes

                    x = MyStromDevice.from_announcement(data, addr[0])
                    log(x)
                except socket.timeout:
                    pass
        except KeyboardInterrupt:
            pass
