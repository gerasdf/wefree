import json
import unittest
from datetime import datetime

import web


class WebBaseTestCase(unittest.TestCase):

    def setUp(self):
        self.app = web.app.test_client()

class TestGet(WebBaseTestCase):
    def test_get_one_sample(self):
        rv = self.app.get('/get')
        self.assertEqual(rv.status_code, 200)

        for line in rv.data.split("\n"):
            data = json.loads(line)
            self.assertEqual(data.keys(), web.sample.keys())

class TestReport(WebBaseTestCase):
    def test_post_report(self):
        rv = self.app.post('/report', data=json.dumps(web.report_sample), content_type="application/json")
        self.assertEqual(rv.status_code, 200)

    def test_post_report_empty(self):
            rv = self.app.post('/report', data="{}", content_type="application/json")
            self.assertEqual(rv.status_code, 418)

class IntegrationTest(WebBaseTestCase):
    def test_post_and_retrieve(self):
        report = {
            'essid': 'spam',
            'bssid': 'EE:00:FF:00:EE:00',
            'password': 'test_password',
            'success': True,
        }
        rv = self.app.post('/report', data=json.dumps(report), content_type="application/json")
        self.assertEqual(rv.status_code, 200)

        rv = self.app.get('/get')
        self.assertEqual(rv.status_code, 200)
        for line in rv.data.split("\n"):
            data = json.loads(line)
            self.assertEqual(data.keys(), web.sample.keys())
            if data["essid"] == "spam":
                break
        else:
            self.assertTrue(False)


if __name__ == "__main__":
    unittest.main()
