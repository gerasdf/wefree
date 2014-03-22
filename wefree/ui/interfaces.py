import NetworkManager
from dbus import DBusException

class WifiSignal(object):
    def __init__(self, device, ap):
        self.bssid = ap.HwAddress
        self.ssid  = ap.Ssid
        self.level = ord(ap.Strength) / 100.0
        self.encrypted = (ap.WpaFlags != 0) or (ap.RsnFlags != 0)
        self.connected = device.SpecificDevice().ActiveAccessPoint.HwAddress == self.bssid
        self.passwords = []
        self.load_passwords()

    def is_connected(self):
        return self.connected

    def load_passwords(self):
        "Load passwords from DB or Cache"
        #for password in PasswordsManager.get_passwords_for(self.bssid):
        #    self.add_password(password)

    def add_password(self, password):
        self.passwords.append(password)

    def has_password(self):
        return 0 != len(self.passwords)

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


