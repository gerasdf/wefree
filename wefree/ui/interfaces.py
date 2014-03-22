import NetworkManager
from dbus import DBusException

class WifiSignal(object):
    def __init__(self, device, ap):
        self.bssid = ap.HwAddress
        self.ssid  = ap.Ssid
        self.level = ord(ap.Strength) / 100.0
        self.encrypted = (ap.WpaFlags != 0) or (ap.RsnFlags != 0)
        self.connected = device.SpecificDevice().ActiveAccessPoint.HwAddress == self.bssid
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
                    print "Found connection"
            except KeyError:
                pass

        return answer

    def load_local_passwords(self):
        connections = self.find_connections()
        for connection in connections:
            try:
                secrets = connection.GetSecrets()
                for secret in secrets['802-11-wireless-security'].values():
                    self.add_local_password(secret)
            except KeyError:
                pass

    def load_db_passwords(self):
        pass
        #for password in PasswordsManager.get_passwords_for(self.bssid):
        #    self.add_password(password)

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

    def connect(self):
        print "Requested connection to %s" % self.ssid

class WifiInterfaces(object):
    """Handle the wifi stuff."""

    def get_ap(self, ssid):
        signals = self.get_signals()
        for signal in signals:
            if ssid == signal.ssid:
                return signal

        return None

    def get_signals(self):
        """Get the wifi signals."""
        all_devs = NetworkManager.NetworkManager.GetDevices()

        signals = []
        for device in all_devs:
            try:
                access_points = device.SpecificDevice().GetAccessPoints()
            except DBusException:
                # not really a wifi one
                continue

            for ap in access_points:
                signal = WifiSignal(device, ap)
                signals.append(signal)

        return signals


