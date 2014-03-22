from django.test import TestCase, RequestFactory
from models import AP, Report
from views import get, report_sample, sample
from datetime import datetime
import json


class TestCores(TestCase):

    def setUp(self):
        self.aps = [ AP(bssid="wefreenetworkessid", essid="A0:F3:C1:86:15:0D"), AP(bssid="weefreenetworkwrongpassword", essid="A0:F3:C1:86:15:0D") ]
        for ap in self.aps:
            ap.save()
        self.reports = [ Report(ap=self.aps[0],password=pwd,date=datetime.now(),success=pwd,geo_lat=0.0,geo_long=0.0) for pwd in ['weefreenetworkwrongpassword', 'weefreenetworkpassword'] ]
        self.reports.append( Report(ap=self.aps[1],password="wrong_password",date=datetime.now(),success=True,geo_lat=0.0,geo_long=0.0) )
        for r in self.reports:
            r.save()

    def test_get_one_sample(self):
        rv = self.client.get('/get/')
        self.assertEqual(rv.status_code, 200)
        body = unicode(rv).split("\n")[3:-1]
        
        index = 0
        for line in body:
            data = json.loads(line)
            self.assertIn(u'positions', data)
            self.assertIn(u'passwords', data)
            self.assertEqual(data[u'essid'], self.aps[index].essid)
            self.assertEqual(data[u'bssid'], self.aps[index].bssid)
            index += 1

    def test_post_report(self):
        rv = self.client.post('/report/', data=json.dumps(report_sample), content_type="application/json")
        self.assertEqual(rv.status_code, 200)

    def test_post_report_empty(self):
            rv = self.client.post('/report/', data="{}", content_type="application/json")
            self.assertEqual(rv.status_code, 418)

    def test_post_and_retrieve(self):
        report = {
            'essid': 'spam',
            'bssid': 'wefreenetworkessid',
            'password': ['test_password'],
            'success': True,
            'lat': 0.0,
            'long': 0.0
        }
        rv = self.client.post('/report/', data=json.dumps(report), content_type="application/json")
        self.assertEqual(rv.status_code, 200)

        rv = self.client.get('/get/')
        self.assertEqual(rv.status_code, 200)
        body = unicode(rv).split("\n")[3:-1]
        index = 0
        for line in body:
            data = json.loads(line)
            self.assertIn(u'positions', data)
            self.assertIn(u'passwords', data)
            if index < len(self.aps) and data["essid"] != self.aps[index].essid:
                if data["essid"] == report["essid"]:
                    break
                else:
                    self.assertTrue(False)
            index += 1
    