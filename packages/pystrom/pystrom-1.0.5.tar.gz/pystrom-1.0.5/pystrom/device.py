# Rafael Urben, 2021
#
# https://github.com/rafaelurben/python-mystrom

import requests

class MyStromDevice():
    DEVICE_TYPES = {
        101: "Switch CH v1",
        102: "Bulb",
        103: "Button+",
        104: "Button",
        105: "LED strip",
        106: "Switch CH v2",
        107: "Switch EU",
    }
    all_devices = {}

    def __init__(self, ip, mac=None, device_type=None):
        self.ip = ip
        self.mac = mac
        self.device_type = device_type
        self.name = self.type_name

        self.all_devices[mac] = self

        self.update_info()

    @classmethod
    def from_announcement(cls, data, ip):
        mac = data[:6].hex()
        device_type = data[6]
        #device_type_2 = data[7]

        if not mac in cls.all_devices:
            return cls(ip=ip, mac=mac, device_type=device_type)
        else:
            return cls.all_devices[mac]

    @property
    def type_name(self):
        if self.device_type in self.DEVICE_TYPES:
            return self.DEVICE_TYPES[self.device_type]
        else:
            return f"Non-MyStrom-Device ({str(self.device_type)})"


    def __str__(self):
        return f"<MyStromDevice '{self.type_name}' {self.mac} @ {self.ip}>"

    # API General

    def api_get(self, path, headers={}):
        path = path.lstrip("/")
        r = requests.get(f"http://{self.ip}/{path}", headers=headers)
        try:
            return r.json()
        except:
            return r.text

    def api_post(self, path, data, headers={}):
        path = path.lstrip("/")
        r = requests.post(f"http://{self.ip}/{path}", payload=data, headers=headers)
        try:
            return r.json()
        except:
            return r.text

    # API Advanced

    def update_info(self):
        data = self.api_get("api/v1/info")
        self.mac = data["mac"]
        self.ip = data["ip"]
        self.version = data["version"]
        self.device_type = data["type"]
        return data

    def get_wifi_list(self):
        data = self.api_get("api/v1/scan")
        networks = {}
        for i in range(len(data)//2):
            networks[data[i*2]] = data[i*2+1]
        return networks

    # Switch

    def switch_on(self):
        return self.api_get("relay?state=1")

    def switch_off(self):
        return self.api_get("relay?state=0")

    def switch_toggle(self):
        return self.api_get("toggle")

    def switch_report(self):
        return self.api_get("report")

