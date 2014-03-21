import json
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from models import AP

sample = {
    'essid': 'wefreenetworkessid',
    'bssid': 'A0:F3:C1:86:15:0D',
    'passwords': ['weefreenetworkwrongpassword', 'weefreenetworkpassword']
}

report_sample = {
    'essid': 'weefreenetworkwrongpassword',
    'bssid': 'A0:F3:C1:86:15:0D',
    'password': 'wrong_password',
    'success': True,
}

def stream_response(request):
    resp = StreamingHttpResponse(stream_response_generator())
    return resp

def stream_response_generator():
    aps = AP.objects.all().select_related()
    for ap in aps:
        data = {"essid": ap.essid, "bssid": ap.bssid, "passwords": [pwd for pwd in ap.report_set.filter(success=True)]}
        yield json.dumps(data)

def index(request):
    return HttpResponse("WeeFree")

def get(request):
    return stream_response(request)

def report(request):
    if not request.method == "POST":
            return HttpResponse("{'message': 'bad json'}", status=418, mimetype="application/json")

    data = json.loads(request.body)
    if not (set(data.keys()) == set(report_sample.keys())):
            return HttpResponse("{'message': 'invalid keys'}", status=418, mimetype="application/json")

    ap = AP.objects.get_or_create(bssid=data["bssid"], essid=data["essid"])

    report = Report.objects.create(ap=ap, password=data["password"], success=data["success"])

    return HttpResponse("")
