import time

class AP(object):
    CRYPTO_OPEN    = 0
    CRYPTO_WEP     = 1
    CRYPTO_WPA2    = 2
    CRYPTO_UNKNOWN = 3

    def __init__(self, ssid, bssid, crypto):
        self.ssid   = ssid
        self.bssid  = bssid
        self.crypto = crypto
    
    def __eq__(self, ap2):
        return self.bssid == ap2.bssid and self.ssid == ap2.ssid

    def __str__(self):
        return "AP: %s/%s" % (self.ssid, self.bssid)
    
    def __repr__(self):
        return str(self)
    
class VisibleSignal(object):
    " There's an os specific abstraction for each Networking implementation "
    def __init__(self, ap, strength = None):
        self.ap = ap
        self.strength = strength
    
    def connect(self, using_password = None):
        """ Will try to connect to the signal using the suplied password.
            If password is not supplied, all ap.possible_passwords will be tried
            (and reported on)"""
        raise Exception, "Subclass responsibility"
    
    def is_connected(self):
        " Answers whether this signal is currently connected or not "
        raise Exception, "Subclass responsibility"
    
class Configuration(object):
    def __init__(self, ap, passwords = None):
        self.ap = ap
        self.passwords = passwords
    
class Report(object):
    TYPE_SUCCESS  = 0
    TYPE_FAILURE  = 1
    TYPE_IMPORTED = 2
    TYPE_UNKNOWN  = 3
    
    def __init__(self, ap, password = None, reporting = TYPE_UNKNOWN):
        self.ap = ap
        self.password = password
        self.reporting = reporting
        self.time_stamp = time.gmtime()

class Location(object):
    def __init__(self, lat = None, _long = None):
        self.lat = lat
        self.long = _long
    
    def is_unknown(self):
        return self.lat is None or self.long is None