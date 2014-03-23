import NetworkManager
from dbus import DBusException

from wefree.passwords_manager import PM
import uuid

class WifiSignal(object):
    def __init__(self, device, ap):
        self.device = device
        self.ap     = ap
        self.bssid = ap.HwAddress
        self.ssid  = ap.Ssid
        self.WpaFlags = ap.WpaFlags
        self.RsnFlags = ap.RsnFlags
        self.level = ord(ap.Strength) / 100.0
        self.pending_password = None
        self.encrypted = (ap.WpaFlags != 0) or (ap.RsnFlags != 0)
        try:
            self.connected = device.SpecificDevice().ActiveAccessPoint.HwAddress == self.bssid
        except AttributeError:
            self.connected = False
        self.db_passwords = []
        self.local_passwords = []

        self.load_local_passwords()
        self.load_db_passwords()

        print "All passwords for %s = %r" % (self.ssid, self.passwords())

    def is_connected(self):
        return self.connected

    def find_connections(self):
        answer = []
        for connection in NetworkManager.Settings.ListConnections():
            settings = connection.GetSettings()
            try:
                if settings['802-11-wireless']['ssid'] == self.ssid:
                    answer.append(connection)
            except KeyError:
                pass

        return answer

    def find_or_create_or_update_connection(self, passphrase):
        connections = self.find_connections()
        seen = []
        for connection in connections:
            seen_bssids = connection.GetSettings()
            seen_bssids = seen_bssids.get('802-11-wireless', {})
            seen_bssids = seen_bssids.get('seen-bssids', [])
            if (self.bssid in seen_bssids) or not seen_bssids:
                seen.append(connection)

        if len(seen) > 0:
            connections = connections[0]
            settings = connection.GetSettings()
            if settings.has_key('ipv4'): del settings['ipv4']
            if settings.has_key('ipv6'): del settings['ipv6']
        else:
            settings = {
                '802-11-wireless': {'ssid':self.ssid},
                'connection': {'id':'WeFree '+self.ssid, 'type':'802-11-wireless', 'uuid':str(uuid.uuid4())},
                }
            connection = NetworkManager.Settings.AddConnection(settings)
        settings = self.update_security_settings(settings, passphrase)
        connection.Update(settings)
        return connection

    def load_local_passwords(self):
        connections = self.find_connections()
        for connection in connections:
            try:
                secrets = connection.GetSecrets()
                for secret in secrets['802-11-wireless-security'].values():
                    self.add_local_password(secret)
            except KeyError:
                pass
            except DBusException:
                pass

    def load_db_passwords(self):
        for password in PM.get_passwords_for_essid(self.ssid):
            self.add_password(password)

    def add_local_password(self, password):
        print "Found password %s" % password
        self.local_passwords.append(password)

    def add_password(self, password):
        self.db_passwords.append(password)

    def has_local_passwords(self):
        return 0 != len(self.local_passwords)

    def has_db_passwords(self):
        return 0 != len(self.db_passwords)

    def has_password(self):
        return self.has_local_passwords() or self.has_db_passwords()

    def passwords(self):
        return self.local_passwords + self.db_passwords

    def update_security_settings(self, settings, passphrase = ''):
        flags = self.WpaFlags | self.RsnFlags

        if flags:
            if flags | NetworkManager.NM_802_11_AP_SEC_KEY_MGMT_PSK:
                security = {
                    "key-mgmt": "wpa-psk",
                    "psk": passphrase,
                }
            else:
                security = {
                    "key": passphrase,
                }
            ochoonce = settings.get("802-11-wireless", {})
            ochoonce.update({ "security": "802-11-wireless-security" })
            settings['802-11-wireless'] = ochoonce
            settings['802-11-wireless-security'] = security
        return settings

    def device_state_changed(self, *args):
        print args

    def connect(self):

        if self.has_password():
            passphrase = self.passwords()[0]
        else:
            passphrase = ''
        print "Requested connection to %s with passphrase: %r" % (self.ssid, passphrase)

        connection = self.find_or_create_or_update_connection(passphrase)

        NetworkManager.NetworkManager.ActivateConnection(connection, self.device, self.ap)
        print "Connection in progress!"

class WifiInterfaces(object):
    """Handle the wifi stuff."""

    def __init__(self):
        #NetworkManager.Settings.connect_to_signal("NewConnection", self.new_connection)
        pass

    def new_connection(self, *args, **kargs):
        print args
        print kargs

    def get_signals(self):
        """Get the wifi signals."""

        all_devs = NetworkManager.NetworkManager.GetDevices()

        signals = []
        for device in all_devs:
            try:
                dev = device.SpecificDevice()
                # dev.RequestScan({})
                access_points = dev.GetAccessPoints()
            except DBusException:
                # not really a wifi one
                # we could check the Type, but this is just fine
                continue

            for ap in access_points:
                signal = WifiSignal(device, ap)
                signals.append(signal)

        return signals

    def force_rescan(self):
        for device in NetworkManager.NetworkManager.GetDevices():
            dev = device.SpecificDevice()
            if isinstance(dev, NetworkManager.Wireless):
                dev.RequestScan({})

