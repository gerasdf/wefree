import dbus
from dbus import DBusException
from wefree import model

try:
    import NetworkManager
    import uuid
except (DBusException, ImportError):
    pass

class NetworkingBackend(object):
    def __init__(self):
        self.pending_signal = None
        self.update_connected_state = lambda x:None

    def device_state_changed(self, new_state, *args, **kwargs):
        if self.pending_signal:
            if self.CONNECTED_STATE == new_state:
                if self.pending_signal.report_to_db:
                    password = self.pending_signal.passwords()[0]
#                    PM.report_success(self.pending_signal.ssid, self.pending_signal.bssid, password, success = True)
                self.pending_signal.report_to_db = False
                self.pending_signal = None
            elif self.FAILED_STATE == new_state:
                self.pending_signal = None
                self.report_to_db = False
        self.update_connected_state(new_state == self.CONNECTED_STATE)

    def register_events(self, update_connected_state, refresh_menu_items):
        self.update_connected_state = update_connected_state
    
    def connect(self, signal):
        self.pending_signal = signal
        signal.connect()

    def is_connected(self, ap):
        return ap in self.currently_connected_aps()
    
    def currently_connected_aps(self):
        " Answers a list of the configurations that're currently active and connected "
        raise Exception, "Subclass responsibility"

    def existing_configurations(self):
        " Answers a list of all connections' configurations saved in the computer "
        raise Exception, "Subclass responsibility"

# NetworkManager implementation

class NetworkManagerVisibleSignal(model.VisibleSignal):
    def __init__(self, ap, strength=None, device = None):
        model.VisibleSignal.__init__(self, ap, strength=strength)
        self.device = device
    
    def connect(self, using_password=None):
        raise Exception, 'Not implemented yet'
    
class NetworkManagerBackend(NetworkingBackend):
    @staticmethod
    def is_installed():
        try:
            NetworkManager.NetworkManager.state()
            return True
        except DBusException:
            return False

    def __init__(self):
        NetworkingBackend.__init__(self)
        self.CONNECTED_STATE = NetworkManager.NM_DEVICE_STATE_ACTIVATED
        self.FAILED_STATE = NetworkManager.NM_DEVICE_STATE_FAILED

    def register_events(self, update_connected_state, refresh_menu_items):
        NetworkingBackend.register_events(self, update_connected_state, refresh_menu_items)
        for device in NetworkManager.NetworkManager.GetDevices():
            device.connect_to_signal("AccessPointAdded", refresh_menu_items)
            device.connect_to_signal("AccessPointRemoved", refresh_menu_items)
            device.connect_to_signal("StateChanged", self.device_state_changed, sender_keyword=device)

    def wifi_devices(self):
        all_devices = NetworkManager.NetworkManager.GetDevices()
        return [device for device in all_devices if device.DeviceType == NetworkManager.NM_DEVICE_TYPE_WIFI]

    def AP_from_native(self, network_manager_AP):
        if (network_manager_AP.WpaFlags | network_manager_AP.RsnFlags):
            # ToDo: use constants like NM_802_11_AP_SEC_KEY_MGMT_PSK:
            crypto = model.AP.CRYPTO_WPA2
        else:
            crypto = model.AP.CRYPTO_OPEN

        ap = model.AP(network_manager_AP.Ssid, network_manager_AP.HwAddress, crypto)
        return ap

    def visible_signals(self):
        """Get the wifi currently visible signals."""
        answer = []
        for device in self.wifi_devices():
            nm_aps = device.SpecificDevice().GetAccessPoints()
            for nm_ap in nm_aps:
                ap = self.AP_from_native(nm_ap)
                strength = ord(nm_ap.Strength) / 100.0
                signal = NetworkManagerVisibleSignal(ap, strength, device)
                answer.append(signal)
        return answer

    def currently_connected_aps(self):
        answer = []
        for device in self.wifi_devices():
            nm_ap = device.SpecificDevice().ActiveAccessPoint
            answer.append(self.AP_from_native(nm_ap))
        return answer

    def existing_configurations(self):
        answer = []
        for connection in NetworkManager.Settings.ListConnections():
            settings = connection.GetSettings()
            try:
                if settings['802-11-wireless']['ssid'] == self.ssid:
                    answer.append(connection)
            except KeyError:
                pass
    
# Wicd implementation

class WicdVisibleSignal(model.VisibleSignal):
    def connect(self, using_password=None):
        raise Exception, 'Not implemented yet'
    
    def is_connected(self):
        raise Exception, 'Not implemented yet'
    
class WicdBackend(NetworkingBackend):
    @staticmethod
    def is_installed():
        try:
            dbus.SystemBus().get_object('org.wicd.daemon','/org/wicd/daemon/wireless')
            return True
        except DBusException:
            return False

    def __init__(self):
        NetworkingBackend.__init__(self)
        self.CONNECTED_STATE = 2
        self.FAILED_STATE = 0
        self.bus = dbus.SystemBus()
        self.wireless = dbus.Interface(
            self.bus.get_object('org.wicd.daemon',
                                '/org/wicd/daemon/wireless'),
            'org.wicd.daemon.wireless'
        )

    def register_events(self, update_connected_state, refresh_menu_items):
        NetworkingBackend.register_events(self, update_connected_state, refresh_menu_items)
        self.bus.add_signal_receiver(self.device_state_changed,
                                     'StatusChanged','org.wicd.daemon',
                                     'org.wicd.daemon', '/org/wicd/daemon')
        self.bus.add_signal_receiver(refresh_menu_items,
                                     'SendEndScanSignal',
                                     'org.wicd.daemon.wireless',
                                     'org.wicd.daemon',
                                     '/org/wicd/daemon/wireless')


if NetworkManagerBackend.is_installed():
    Networking = NetworkManagerBackend()
elif WicdBackend.is_installed():
    Networking = WicdBackend()

print