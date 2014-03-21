import netifaces
import wifi

class WifiInterface(object):
    """Handle the wifi stuff."""

    def get_signals(self):
        """Get the wifi signals."""
        signals = []
        for interface in netifaces.interfaces():
            try:
                cells = wifi.Cell.all(interface)
            except wifi.exceptions.InterfaceError:
                # not really a wifi one
                continue

            for cell in cells:  # a little hardcoded
                # FIXME: here we need to check, even if it's encrypted,
                # if we have the password!!
                have_pass = not cell.encrypted
                _vals = map(int, cell.quality.split("/"))
                level = _vals[0] / _vals[1]
                name = cell.ssid

                signals.append((level, name, have_pass))
        return signals


