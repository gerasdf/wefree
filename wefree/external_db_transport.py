# -*- coding: utf-8 -*
import unittest
import requests
import json
from base64 import decodestring

class Mock(object):
    last_url_made = None

    @classmethod
    def mockear_requests_get(cls, headers, text):
        def my_get(url, *args, **kwargs):
            class Response(object):
                pass
            r = Response()
            r.headers, r.text = headers, text
            cls.last_url_made = url
            return r
        requests.get = my_get


class ZonaGratisBrDbTransport():
    base_url = 'http://www.zonagratis.com.br/api/get/hotspot/'

    def get_nearby(self, lat, lon, max_results=0):
        url = self.base_url + 'nearby?lat=' + lat + '&lon=' + lon
        if max_results != 0:
            url += '&max_results=' + max_results
        return self.get_base(url)

    def get_area(self, lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat, max_results=0):
        url = self.base_url + 'area?lower_left_lon=' + lower_left_lon + \
                '&lower_left_lat=' + lower_left_lat + '&upper_right_lon=' + \
                upper_right_lon + '&upper_right_lat=' + upper_right_lat
        if max_results != 0:
            url += '&max_results=' + max_results
        return self.get_base(url)

    def get_base(self, url):
        return requests.get(url).text

    def decode(self, encripted_and_base64):
        encripted = decodestring(encripted_and_base64)
        answer = ''
        l = len(encripted)
        key = encripted[:3]
        for j in range(3,len(encripted)):
            answer += chr(ord(encripted[j]) ^ ord(key[(j-3) % 3]))
        return answer


class TestsDbTransport(unittest.TestCase):
    report_near = "{'hotspots':[{'mac':'f4:ec:38:ce:9a:98','ssid':'LaReservaAP2','lat':-38.1006252,'lon':-57.5472497,'days_ago':19,'count':1,'rating':1.0,'apk':88,'name':'','address':'Calle 1 4299-4399, Mar del Plata/Argentina - Buenos Aires','create_time':1393704587265,'last_access_time':1393797532154,'count_access':3,'likes':0,'dislikes':0,'open':true,'shared':false,'has_internet':true,'alertType':'NO_PROBLEM','score':303},{'mac':'00:0f:02:44:6f:90','ssid':'Wireless-N Router','lat':-38.08700244,'lon':-57.54191148,'days_ago':29,'count':1,'rating':1.0,'apk':122,'name':'','address':'Av Martínez de Hoz 4899-4999, Mar del Plata/Argentina - Buenos Aires','create_time':1389379651655,'last_access_time':1392888556172,'count_access':4,'likes':0,'dislikes':0,'open':true,'shared':false,'has_internet':true,'alertType':'NO_INFO','score':-1582324309}],'env':'PROD','success':true,'ms':11.985,'clock':1395444336377}"
    report_area = "{'number_of_networks':16,'total_open_networks':2107184,'networks':[{'mac':'2 wifis','ssid':'2 wifis','lat':12.3304771,'lon':18.808376250000002,'days_ago':0,'count':2,'rating':1.0},{'mac':'14 wifis','ssid':'14 wifis','lat':12.183068304014,'lon':14.279568278707197,'days_ago':0,'count':14,'rating':1.0}],'env':'PROD','success':true,'ms':5252.913,'clock':1395446000809}"

    report_near_url = 'http://www.zonagratis.com.br/api/get/hotspot/nearby?lat=-64.5012528&lon=-31.057253&max_results=2'
    report_area_url = 'http://www.zonagratis.com.br/api/get/hotspot/area?lower_left_lon=10&lower_left_lat=10&upper_right_lon=20&upper_right_lat=20&max_results=2'

    def test_get_nearby(self):
        Mock.mockear_requests_get({"content-type":"application/json"}, self.report_near)

        d = ZonaGratisBrDbTransport()
        v = d.get_nearby(lon='-31.057253',lat='-64.5012528',max_results='2')

        self.assertEqual(v, self.report_near)
        self.assertEqual(Mock.last_url_made, self.report_near_url)

    def test_get_area(self):
        Mock.mockear_requests_get({"content-type":"application/json"}, self.report_area)

        d = ZonaGratisBrDbTransport()
        v = d.get_area(lower_left_lon='10',lower_left_lat='10',upper_right_lon='20',upper_right_lat='20',max_results='2')

        self.assertEqual(v, self.report_area)
        self.assertEqual(Mock.last_url_made, self.report_area_url)

if __name__ == '__main__':
    unittest.main()
