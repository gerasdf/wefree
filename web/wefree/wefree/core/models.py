from django.db import models
import json


class AP(models.Model):
    bssid = models.CharField(max_length=25)
    essid = models.CharField(max_length=128)
    creation_date = models.DateTimeField(auto_now_add=True)

    def to_json(self):
        reports = self.report_set.filter(success=True)
        data = {
            "essid": self.essid, "bssid": self.bssid,
            "passwords": [report.password for report in reports],
            "positions": [(report.geo_lat, report.geo_long) for report in reports]
        }
        return json.dumps(data)


class Report(models.Model):
    ap = models.ForeignKey(AP)
    password = models.CharField(max_length=128)
    date = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField()
    geo_lat = models.FloatField(null=True)
    geo_long = models.FloatField(null=True)
