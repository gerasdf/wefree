import unittest
import requests
import json

from mocker import Mocker, MockerTestCase

class DbTransport ():
    def __init__(self, server_ip = '127.0.0.1'):
        self.server_ip = server_ip;

    def get_db_data (self):
        r = requests.get('http://' + self.server_ip + '/get/')
        if (r.headers["content-type"] != "application/json"):
            raise ValueError
        return r.text

    def set_ap_on_db(self, data):
        return requests.post('http://' + self.server_ip + '/report/', data=data, headers={"content-type":"application/json"})

class MockerTestsDbTransport(MockerTestCase):
    report = "{'essid': 'spam','bssid': 'EE:00:FF:00:EE:00','password': 'test_password','success': True,'lat':29.29,'long':10.10,}"
    def test_get_db_data_ok (self):
        result = self.mocker.mock()
        result.text
        self.mocker.result(self.report)
        result.headers
        self.mocker.result({"content-type":"application/json"})

        myget = self.mocker.replace("requests.get")
        myget('http://127.0.0.1/get/')
        self.mocker.result(result)

        self.mocker.replay()

        d = DbTransport()
        v = d.get_db_data()

        self.assertEqual(v, self.report)
        self.mocker.verify()

    def test_get_db_data_error (self):
        result = self.mocker.mock()
        result.text
        self.mocker.result(self.report)
        result.headers
        self.mocker.result({"content-type":"application/json"})

        myget = self.mocker.replace("requests.get")
        myget('http://127.0.0.1/get/')
        self.mocker.result(result)

        self.mocker.replay()

        d = DbTransport()
        v = d.get_db_data()

        self.assertEqual(v, self.report)
        self.mocker.verify()

class UnittestsDbTransport(unittest.TestCase):
    def setUp (self):
        self.db_transport = DbTransport()

    def test_default_server_ip (self):
        self.assertEqual(self.db_transport.server_ip, '127.0.0.1')
        self.assertNotEqual(self.db_transport.server_ip, '127.0.1.1')

    def test_post_ap(self):
        report = {
            'essid': 'spam',
            'bssid': 'EE:00:FF:00:EE:00',
            'password': 'test_password',
            'success': True,
        }

        self.db_transport.set_ap_on_db(json.dumps(report))

if __name__ == '__main__':
    unittest.main()
