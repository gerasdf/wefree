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
        return 0 == len(self.passwords)

class WifiInterface(object):
    """Handle the wifi stuff."""

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
                encrypted = ap.WpaFlags or ap.RsnFlags
                signal = WifiSignal(name, level, encrypted)
                signals.append(signal)

        return signals


