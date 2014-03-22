import unittest
import requests
import json

class DbTransportError(Exception):
    pass

class DbTransport(object):
    GET_URL = 'http://%s/get/'
    REPORT_URL = 'http://%s/report/'

    def __init__(self, server_ip = '127.0.0.1'):
        self.server_ip = server_ip

    def get_db_data(self):
        try:
            r = requests.get(self.GET_URL % self.server_ip)
        except Exception as e:
            raise DbTransportError(unicode(e))
        if r.status_code != 200:
            raise DbTransportError("status %d. Error: %s" % (r.status_code, r.text))
        if (r.headers["content-type"] != "application/json"):
            raise DbTransportError("bad content type")
        return r.text

    def set_ap_on_db(self, data):
        try:
            r = requests.post(self.REPORT_URL % self.server_ip , data=data, headers={"content-type":"application/json"})
        except Exception as e:
            raise DbTransportError(unicode(e))
        if r.status_code != 200:
            raise DbTransportError("status %d. Error: %s" % (r.status_code, r.text))


