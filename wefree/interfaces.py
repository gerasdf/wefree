import dbus
from dbus import DBusException

from wefree.passwords_manager import PM, AP
import uuid

USE_NETWORK_MANAGER=True
try:
    import NetworkManager
except (DBusException, ImportError):
    USE_NETWORK_MANAGER=False


class WifiSignalBase(object):
    def __init__(self):
        self.db_passwords = []
        self.local_passwords = []
        self.report_to_db = False

    def is_connected(self):
        return self.connected

    def add_db_password(self, password):
        self.db_passwords.append(password)

    def add_password(self, password, report = False):
        self.report_to_db = report
        if report:
            self.add_db_password(password)
        else:
            self.local_passwords.append(password)

    def has_local_passwords(self):
        return 0 != len(self.local_passwords)

    def has_db_passwords(self):
        return 0 != len(self.db_passwords)

    def has_password(self):
        return self.has_local_passwords() or self.has_db_passwords()

    def passwords(self):
        return self.local_passwords + self.db_passwords

    def _load_db_passwords(self):
        for password in PM.get_passwords_for_essid(self.ssid):
            self.add_db_password(password)

    def _add_local_password(self, password):
        print "Found password %s" % password
        self.local_passwords.append(password)

    def connect(self):
        raise BaseException("Not implemented")

    def load_passwords(self):
        self._load_local_passwords()
        self._load_db_passwords()

        print "All passwords for %s = %r" % (self.ssid, self.passwords())


class WifiSignalNetworkManager(WifiSignalBase):
    def __init__(self, device, ap):
        super(WifiSignalNetworkManager, self).__init__()
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
        self.load_passwords()

    def _find_connections(self):
        answer = []
        for connection in NetworkManager.Settings.ListConnections():
            settings = connection.GetSettings()
            try:
                if settings['802-11-wireless']['ssid'] == self.ssid:
                    answer.append(connection)
            except KeyError:
                pass

        return answer

    def _find_or_create_or_update_connection(self, passphrase):
        connections = self._find_connections()
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

    def _load_local_passwords(self):
        connections = self._find_connections()
        for connection in connections:
            try:
                secrets = connection.GetSecrets()
                for secret in secrets['802-11-wireless-security'].values():
                    self._add_local_password(secret)
            except KeyError:
                pass
            except DBusException:
                pass

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

    def connect(self):
        if self.has_password():
            passphrase = self.passwords()[0]
        else:
            passphrase = ''
        print "Requested connection to %s with passphrase: %r" % (self.ssid, passphrase)

        connection = self._find_or_create_or_update_connection(passphrase)
        NetworkManager.NetworkManager.ActivateConnection(connection, self.device, self.ap)
        print "Connection in progress!"


class WifiSignalWicd(WifiSignalBase):
    def __init__(self, wireless, network_id):
        super(WifiSignalWicd, self).__init__()
        self.network_id = network_id
        self.wireless = wireless
        self.bssid = str(self._getProperty('bssid'))
        self.ssid = str(self._getProperty('essid'))
        self.level = int(self._getProperty('quality'))
        self.connected = self.wireless.GetApBssid() == self.bssid
        self.encrypted = self._getProperty('encryption')
        self.load_passwords()

    def _getProperty(self, _property):
        return self.wireless.GetWirelessProperty(self.network_id, _property)

    def _setProperty(self, _property, value):
        return self.wireless.SetWirelessProperty(self.network_id, _property, value)

    def _load_local_passwords(self):
        key = self._getProperty("key")
        if key:
            self._add_local_password(key)

    def connect(self):
        if self.has_password():
            passphrase = self.passwords()[0]
        else:
            passphrase = ''
        print "Requested connection to %s with passphrase: %r" % (self.ssid, passphrase)
        self._setProperty("key", passphrase)
        self.wireless.ConnectWireless(self.network_id)


class WifiInterfacesBase(object):
    def __init__(self):
        self.pending_signal = None
        self.update_connected_state = lambda x:None

    def device_state_changed(self, new_state, *args, **kwargs):
        if self.pending_signal:
            if self.CONNECTED_STATE == new_state:
                if self.pending_signal.report_to_db:
                    password = self.pending_signal.passwords()[0]
                    PM.report_success(self.pending_signal.ssid, self.pending_signal.bssid, password, success = True)
                self.pending_signal.report_to_db = False
                self.pending_signal = None
            elif self.FAILED_STATE == new_state:
                self.pending_signal = None
                self.report_to_db = False
            else:
                print('{!r} -> {!r}'.format(new_state, args))
        self.update_connected_state(  new_state == self.CONNECTED_STATE)

class WifiInterfacesWicd(WifiInterfacesBase):
    def __init__(self):
        super(WifiInterfacesWicd, self).__init__()
        self.bus = dbus.SystemBus()
        self.wireless = dbus.Interface(
            self.bus.get_object('org.wicd.daemon',
                                '/org/wicd/daemon/wireless'),
            'org.wicd.daemon.wireless'
        )
        self.CONNECTED_STATE = 2
        self.FAILED_STATE = 0

    def connect(self, signal):
        self.pending_signal = signal
        signal.connect()

    def get_signals(self):
        signals = []
        for network_id in range(0, self.wireless.GetNumberOfNetworks()):
            signal = WifiSignalWicd(self.wireless, network_id)
            signals.append(signal)
        return signals

    def get_known_networks(self):
        aps = []
        for signal in self.get_signals():
            key = str(signal._getProperty("key"))
            if key:
                aps.append(AP(signal.bssid, signal.ssid, [key]))
        return aps

    def connect_signals(self, refresh_menu_items, update_connected_state):
        self.update_connected_state = update_connected_state
        self.bus.add_signal_receiver(self.device_state_changed,
                                     'StatusChanged','org.wicd.daemon',
                                     'org.wicd.daemon', '/org/wicd/daemon')
        self.bus.add_signal_receiver(refresh_menu_items,
                                     'SendEndScanSignal',
                                     'org.wicd.daemon.wireless',
                                     'org.wicd.daemon',
                                     '/org/wicd/daemon/wireless')

    def force_rescan(self):
        self.wireless.Scan("")

class WifiInterfacesNetworkManager(WifiInterfacesBase):
    """Handle the wifi stuff."""

    def __init__(self):
        super(WifiInterfacesNetworkManager, self).__init__()
        self.pending_signal = None
        self.CONNECTED_STATE = NetworkManager.NM_DEVICE_STATE_ACTIVATED
        self.FAILED_STATE = NetworkManager.NM_DEVICE_STATE_FAILED

    def connect(self, signal):
        self.pending_signal = signal
        signal.connect()

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
                signal = WifiSignalNetworkManager(device, ap)
                signals.append(signal)
        return signals

    def get_known_networks(self):
        answer = []
        for connection in NetworkManager.Settings.ListConnections():
            try:
                settings  = connection.GetSettings()
                ssid      = settings['802-11-wireless']['ssid']
                bssid     = settings['802-11-wireless'].get('seen-bssids', [])
                if not bssid:
                    bssid = None
                else:
                    bssid = bssid[0]
                passwords = connection.GetSecrets()['802-11-wireless-security'].values()
                answer.append(AP(bssid, ssid, passwords))
            except (KeyError, DBusException):
                pass

        return answer

    def connect_signals(self, refresh_menu_items, update_connected_state):
        self.update_connected_state = update_connected_state
        for device in NetworkManager.NetworkManager.GetDevices():
            device.connect_to_signal("AccessPointAdded", refresh_menu_items)
            device.connect_to_signal("AccessPointRemoved", refresh_menu_items)
            device.connect_to_signal("StateChanged", self.device_state_changed, sender_keyword=device)

    def force_rescan(self):
        for device in NetworkManager.NetworkManager.GetDevices():
            dev = device.SpecificDevice()
            if isinstance(dev, NetworkManager.Wireless):
                dev.RequestScan('')


if USE_NETWORK_MANAGER:
    WifiInterfaces = WifiInterfacesNetworkManager
    WifiSignal = WifiSignalNetworkManager
else:
    WifiInterfaces = WifiInterfacesWicd
    WifiSignal = WifiSignalWicd
