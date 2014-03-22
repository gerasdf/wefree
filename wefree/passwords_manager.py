import json
from db_transport import DbTransport
from external_db_transport import ZonaGratisBrDbTransport

"~/.weefree/db"

class PasswordsManager(object):
    def __init__(self, server_address):
        self.state = "NOT_INITIALIZED"
        self.aps_by_bssid = defaultdict(list)
        self.aps_by_essid = defaultdict(list)
        self.server_transport = DbTransport(server_address=server_address)

    def get_passwords_from_server(self):
        data = self.server_transport.get_db_data()
        for line in data:
            ap = json.loads(line)
            if ap["bssid"]:
                self.aps_by_bssid[ap["bssid"]] = ap
            if ap["essid"]:
                self.aps_by_essid[ap["essid"]] = ap

    def get_passwords_for_bssid(bssid):
        passwords = []
        aps = self.aps_by_bssid.get(bssid, None)
        if aps:
            [passwords.extend(ap["passwords"]) for ap in aps]
        return passwords

    def get_passwords_for_essid(bssid):
        passwords = []
        aps = self.aps_by_essid.get(essid, None)
        if aps:
            [passwords.extend(ap["passwords"]) for ap in aps]
        return passwords
