import NetworkManager
from dbus import DBusException

class WifiSignal(object):
    def __init__(self, ssid, level, encrypted):
        self.ssid  = ssid
        self.level = level
        self.encrypted = encrypted
        self.passwords = []

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
                name      = ap.Ssid
                level     = ord(ap.Strength) / 100.0
                encrypted = (ap.WpaFlags != 0) or (ap.RsnFlags != 0)
                signal = WifiSignal(name, level, encrypted)
                signals.append(signal)

        return signals


