#!/bin/python
# -*- coding: utf-8 -*
import sys
from db_transport import DbTransport
from external_db_transport import ZonaGratisBrDbTransport
import logging
import json
import os
from math import cos, sin, pi
from random import uniform
import time


class BulkManager(object):
    def __init__(self):
        self.server_transport = DbTransport(server_address="localhost:3210")
        self.external_transport = ZonaGratisBrDbTransport()

    def streaming_external_passwords_from(self, lon, lat, radius_max=1.0):
        meters = 100.
        radius = 0.1 # min .500 Km
        degree = 0.
        radius_inc = 10. / 360. # 10 Km / in 360º = 0.027 Km = 270m
        while radius < radius_max: # radius_max = 1.0º ~100Km
            time.sleep(3)
            self.transport( lon+cos(degree)*radius , lat+sin(degree)*radius )
            degree_inc = 360. * radius_inc/radius
            radius += radius_inc
            degree += degree_inc
            degree %= 360.
            if degree < 0.01:
                radius = 0.1
                lon = uniform(-180.,180.)
                lat = uniform(-90.,90.)
                print "Changing to %s lat %s lon..." % (lat, lon)
    
    def transport(self, left, top):
        aps = self.get_tail(left, top)
        self.flush_external_passwords_to_server(aps)

    def flush_external_passwords_to_server(self, aps):
        for ap in aps:
            if not ap["open"]:
                data = {
                    "bssid": ap["mac"],
                    "essid": ap["ssid"],
                    "lat": ap["lat"],
                    "long": ap["lon"],
                    "password": self.external_transport.decode(ap["password"]),
                    "success": True, # fixme
                }
                self.server_transport.set_ap_on_db(json.dumps(data))

    def get_tail(self, lon, lat):
        filename = 'tails/lon%s_lat%s.tail' % (unicode(lon).zfill(3), unicode(lat).zfill(2))
        if not os.path.isfile(filename):
            print "Downloading %s..." % filename
            data = self.external_transport.get_nearby(lon=unicode(lon),lat=unicode(lat))
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