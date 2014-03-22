#!/bin/python
# -*- coding: utf-8 -*
import sys
from db_transport import DbTransport
from external_db_transport import ZonaGratisBrDbTransport
import logging
import json
import os
from math import cos, sin

def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step


class BulkManager(object):
    def __init__(self):
        self.server_transport = DbTransport(server_address="http://localhost:3210")
        self.external_transport = ZonaGratisBrDbTransport()

    def streaming_external_passwords_from(self, lon, lat, radius_max=1.0):
        radius_inc = 0.001
        radius = 0
        degree = 0.
        degree_inc = 10.000
        while radius < radius_max:
            self.transport( lon+cos(degree)*radius , lat+cos(degree)*radius )
            radius += radius_inc
            degree += degree_inc
            degree %= 360
    
    def transport(self, left, top):
        aps = self.get_tail(left, top)
        self.flush_external_passwords_to_server(aps)

    def flush_external_passwords_to_server(self, aps):
        for ap in aps:
            if not ap["open"]:
                self.server_transport.set_ap_on_db({
                "bssid": ap["mac"],
                "essid": ap["ssid"],
                "lat": ap["lat"],
                "long": ap["lon"],
                "password": self.external_transport.decode(ap["password"]),
                "success": True, # fixme
                })

    def get_tail(self, lower_left_lon, lower_left_lat):
        filename = 'tails/lon%s_lat%s.tail' % (unicode(lower_left_lon).zfill(3), unicode(lower_left_lat).zfill(2))
        if not os.path.isfile(filename):
            print "Downloading %s..." % filename
            data = self.external_transport.get_nearby(lon=unicode(lower_left_lon),lat=unicode(lower_left_lat))
            with open(filename, 'w') as f:
                f.write(data.encode('utf-8'))
            print "%s saved." % filename
        else:
            with open(filename, 'r') as f:
                data = f.read()
        print "%s synced." % filename
        return json.loads(data)["hotspots"]

if __name__ == '__main__':
    manager = BulkManager()
    lon,lat = sys.argv[1:3]
    manager.streaming_external_passwords_from(float(lon),float(lat))