from django.db import models
import json


class AP(models.Model):
    bssid = models.CharField(max_length=25)
    essid = models.CharField(max_length=128)
    creation_date = models.DateTimeField(auto_now_add=True)

class Report(models.Model):
    ap = models.ForeignKey(AP)
    password = models.CharField(max_length=128)
    date = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField()
