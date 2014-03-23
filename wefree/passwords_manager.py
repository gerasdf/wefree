import os
import json
import logging
import shelve
from collections import defaultdict, namedtuple
from db_transport import DbTransport
from external_db_transport import ZonaGratisBrDbTransport
import thread

Location = namedtuple("Location", ["lat", "long"])

class AP(object):
    def __init__(self, bssid=None, essid=None, passwords=None,
                 locations=None, success=None):
        self.bssid = bssid
        self.essid = essid
        self.passwords = passwords
        self.locations = locations
        self.success = success

    def get_avg_location(self):
        if not self.locations:
            return None
        avg_lat = sum([location.lat for location in self.locations]) / len(self.locations)
        avg_long = sum([location.long for location in self.locations]) / len(self.locations)

        return Location(lat=avg_lat, long=avg_long)

    @classmethod
    def from_json(cls, data_json):
        ap = json.loads(data_json)
        locations = ap.get("positions", [])
        locations = [Location(lat=l[0], long=l[1]) for l in locations]

        return AP(ap.get("bssid"), ap.get("essid"), ap.get("passwords"),
                   locations=locations, success=True)

    def __equal__(self, other):
        return self.bssid == other.bssid and self.essid == other.essid

    def __repr__(self):
        return "<AP %s %s>" % (self.essid, self.bssid)


class GeoLocation(object):
    def __init__(self, password_manager=None):
        self.pm = password_manager
        self.seen_bssids = []

    def refresh_seen_bssids(self, seen_bssids):
        self.seen_bssids = seen_bssids

    def get_location(self):
        avg_lat, avg_long = 0, 0
        seen_and_known = 0
        for seen_bssid in self.seen_bssids:
            aps = self.pm.aps_by_bssid.get(seen_bssid, [])
            for ap in aps:
                location = ap.get_avg_location()
                if location:
                    avg_lat += location.lat
                    avg_long += location.long
                seen_and_known += 1
        if seen_and_known == 0:
            return None

        avg_lat /= seen_and_known
        avg_long /= seen_and_known

        return (avg_lat, avg_long)

class Database(object):
    def __init__(self):
        self.db = shelve.open(os.path.expanduser(("~/.wefree_db")))

    def load(self):
        return self.db.get("aps", [])

    def save(self, aps):
        self.db["aps"] = aps
        self.db.sync()

class PasswordsManager(object):
    def __init__(self, server_address):
        self.aps_by_bssid = defaultdict(list)
        self.aps_by_essid = defaultdict(list)
        self.server_transport = DbTransport(server_address=server_address)
        self.external_transport = ZonaGratisBrDbTransport()
        self.local_db_cache = Database()
        aps = self.local_db_cache.load()
        for ap in aps:
            self.load_ap(ap)

    def load_ap(self, ap):
        if ap.bssid:
            self.aps_by_bssid[ap.bssid].append(ap)
        if ap.essid:
            self.aps_by_essid[ap.essid].append(ap)

    def get_passwords_from_server(self):
        try:
            data = self.server_transport.get_db_data().split("\n")
        except Exception as e:
            logging.error(e)
        else:
            for line in data:
                if not line:
                    continue
                try:
                    ap = AP.from_json(line)
                    self.load_ap(ap)
                except Exception as e:
                    logging.error("Error loading AP from json")
                    logging.error(e)
        self.sync()

    def get_external_passwords(self, geolocation):
        position = geolocation.get_location()
        data = self.external_transport.get_nearby("%s" % position[0], "%s" % position[1])
        aps = json.loads(data)["hotspots"]

        self.external_aps = []
        for ap in aps:
            if not ap["open"]:
                the_ap = AP(ap["mac"], ap["ssid"], self.external_transport.decode(ap["password"]),
                            ap["lat"], ap["lon"], success=True)
                self.external_aps.append(the_ap)

    def upload_report(self, json_data):
        thread.start_new_thread(self.server_transport.set_ap_on_db,
                                (json_data,))

    def get_passwords_for_bssid(self, bssid):
        aps = self.aps_by_bssid.get(bssid, None)
        return self._get_passwords(aps)

    def get_passwords_for_essid(self, essid):
        aps = self.aps_by_essid.get(essid, None)
        return self._get_passwords(aps)

    def _get_passwords(self, aps):
        passwords = []
        if aps:
            [passwords.extend(ap.passwords) for ap in aps]
        return passwords

    def get_passwords_for_ap(self, ap):
        if ap.bssid:
            return self.get_passwords_for_essid(ap.essid)
        else:
            return self.get_passwords_for_bssid(ap.bssid)

    def get_all_aps(self):
        s = set()
        [s.update(set(l)) for l in self.aps_by_bssid.values()]
        [s.update(set(l)) for l in self.aps_by_essid.values()]
        return s

    def sync(self):
        self.local_db_cache.save(self.get_all_aps())

    def add_new_password(self, password, essid=None, bssid=None):
        location = GEO.get_location()
        ap = AP(essid=essid, bssid=bssid, passwords=[password],
                locations=[location], success=True)
        self.load_ap(ap)
        self.sync()
        json_data = json.dumps({
            "essid": essid,
            "bssid": bssid,
            "password": password,
            "lat": location.lat if location else 0, # FIXME
            "long": location.long if location else 0, # FIXME
            "success": True,
        })
        self.upload_report(json_data)

PM = PasswordsManager('page.local:8000')
GEO = GeoLocation(PM)

if __name__ == "__main__":
    pm = PasswordsManager("page.local:8000")
    print(pm.get_passwords_for_bssid("asd"))
    print(pm.get_passwords_for_bssid("58:6d:8f:9d:0b:66"))
    print(pm.get_passwords_for_essid("DelPilar"))

    pm.get_passwords_from_server()
    print(pm.get_passwords_for_bssid("asd"))
    print(pm.get_passwords_for_bssid("58:6d:8f:9d:0b:66"))
    print(pm.get_passwords_for_essid("DelPilar"))

    pm.sync()

    geo = GeoLocation(pm)
    geo.refresh_seen_bssids(["64:70:02:9a:3d:06"])
    print(geo.get_location())

    pm.add_new_password("elpassword", essid="theessid", bssid="mac")
    import time
    time.sleep(3)

