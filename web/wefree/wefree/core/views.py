import json
from django.http import HttpResponse
from django.shortcuts import render
from models import AP, Report

sample = {
    'essid': 'wefreenetworkessid',
    'bssid': 'A0:F3:C1:86:15:0D',
    'passwords': ['weefreenetworkwrongpassword', 'weefreenetworkpassword']
}

report_sample = {
    'essid': 'weefreenetworkwrongpassword',
    'bssid': 'A0:F3:C1:86:15:0D',
    'password': ['wrong_password'],
    'success': True,
    'lat': -32.123,
    'long': 12.343
}

def index(request):
    return HttpResponse("WeeFree")

def get(request):
    ret_data = ""
    aps = AP.objects.all().select_related()
    for ap in aps:
        ret_data += ap.to_json() + "\n"
    return HttpResponse(ret_data, mimetype="application/json")

def report(request):
    if not request.method == "POST":
            return HttpResponse("{'message': 'bad json'}", status=418, mimetype="application/json")

    data = json.loads(request.body)
    if not (set(data.keys()) == set(report_sample.keys())):
            return HttpResponse("{'message': 'invalid keys'}", status=418, mimetype="application/json")

    ap, created = AP.objects.get_or_create(bssid=data["bssid"], essid=data["essid"])

    report = Report(ap=ap, password=data["password"], success=data["success"], geo_lat=data["lat"], geo_long=data["long"])
    report.save()

    return HttpResponse("")
