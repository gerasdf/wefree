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
    return render(request, "core/index.html")

def get(request):
    ret_data = ""
    aps = AP.objects.all().select_related()
    separator = "\n"

    if request.GET.get("nonchunked"):
        ret_data += "["
        separator = ","
    ret_data += separator.join([ap.to_json() for ap in aps])
    if request.GET.get("nonchunked"):
        ret_data += "]"

    return HttpResponse(ret_data, mimetype="application/json")

def report(request):
    if not request.method == "POST":
            return HttpResponse("{'message': 'bad json'}", status=418, mimetype="application/json")

    data = json.loads(request.body)
    if not (set(data.keys()) == set(report_sample.keys())):
            return HttpResponse("{'message': 'invalid keys'}", status=418, mimetype="application/json")

    ap, created = AP.objects.get_or_create(bssid=data["bssid"], essid=data["essid"])

    Report.objects.get_or_create(ap=ap, password=data["password"], success=data["success"], geo_lat=data["lat"], geo_long=data["long"])

    return HttpResponse("")


def comunity_crawl(request):
    return render(request, "core/crawl.html")
