import urllib3
import json
import invoke
import re
from datetime import datetime, timedelta


class Device(object):
    datetime_format = "%Y-%m-%dT%H:%M:%SZ"

    def __init__(
        self,
        name,
        hostname,
        os,
        addresses,
        created,
        expires,
        lastSeen,
        clientVersion,
        updateAvailable,
        **_,  # ignore
    ):
        self.fullname = name
        self.name = self.fullname.split(".")[0]
        self.hostname = hostname
        self.os = os
        self.addresses = addresses

        self.created = datetime.strptime(created, Device.datetime_format) + timedelta(
            hours=2
        )
        self.expires = datetime.strptime(expires, Device.datetime_format) + timedelta(
            hours=2
        )
        self.lastSeen = datetime.strptime(lastSeen, Device.datetime_format) + timedelta(
            hours=2
        )

        self.clientVersion = clientVersion
        self.updateAvailable = updateAvailable

    @property
    def online(self):
        return (datetime.now() - self.lastSeen) < timedelta(minutes=2)


class TailscaleAPI(object):
    minon_filter = ["windows", "linux", "macos", "rasp", "android", "ios"]

    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key

    def list(self, all_devices=False):
        http = urllib3.PoolManager()
        device_url = f"{self.url}/devices"
        headers = urllib3.make_headers(basic_auth=f"{self.api_key}:")
        response = http.request("GET", device_url, headers=headers)
        if response.status != 200:
            raise invoke.exceptions.Exit("Error getting devices!")

        response = json.loads(response.data.decode("utf-8"))
        minon_devices = []
        other_devices = []
        for device in response["devices"]:
            if any([device["name"].startswith(f) for f in TailscaleAPI.minon_filter]):
                minon_devices.append(Device(**device))
            elif all_devices:
                other_devices.append(Device(**device))
        minon_devices.sort(
            key=lambda d: [
                [
                    int(v) if v.isdigit() else v
                    for v in re.match(r"(\D*)(\d*)(.*)", d.name, re.I).groups()
                ]
            ]
        )

        return minon_devices + sorted(other_devices, key=lambda d: d.name)
