import json
from collections import defaultdict
from db_transport import DbTransport
from external_db_transport import ZonaGratisBrDbTransport

"~/.weefree/db"

class GeoLocation(object):

    @staticmethod
    def get_position():
        return (-31.05247, -64.50410)

class PasswordsManager(object):
    def __init__(self, server_address):
        self.state = "NOT_INITIALIZED"
        self.aps_by_bssid = defaultdict(list)
        self.aps_by_essid = defaultdict(list)
        self.server_transport = DbTransport(server_address=server_address)
        self.external_transport = ZonaGratisBrDbTransport()

    def get_passwords_from_server(self):
        data = self.server_transport.get_db_data().split("\n")
        for line in data:
            try:
                ap = json.loads(line)
            except:
                continue
            if ap["bssid"]:
                self.aps_by_bssid[ap["bssid"]].append(ap)
            if ap["essid"]:
                self.aps_by_essid[ap["essid"]].append(ap)

    def get_external_passwords(self):
        position = GeoLocation.get_position()
        data = self.external_transport.get_nearby("%s" % position[0], "%s" % position[1])
        aps = json.loads(data)["hotspots"]

        self.external_aps = []
        for ap in aps:
            if not ap["open"]:
                self.external_aps.append({
                    "bssid": ap["mac"],
                    "essid": ap["ssid"],
                    "lat": ap["lat"],
                    "long": ap["lon"],
                    "password": self.external_transport.decode(ap["password"]),
                    "success": True, # fixme
                    })

    def upload_external_passwords(self):
        self.get_external_passwords()
        for ap in self.external_aps:
            self.server_transport.set_ap_on_db(json.dumps(ap))


    def get_passwords_for_bssid(self, bssid):
        passwords = []
        aps = self.aps_by_bssid.get(bssid, None)
        if aps:
            [passwords.extend(ap["passwords"]) for ap in aps]
        return passwords

    def get_passwords_for_essid(self, essid):
        passwords = []
        aps = self.aps_by_essid.get(essid, None)
        if aps:
            [passwords.extend(ap["passwords"]) for ap in aps]
        return passwords
