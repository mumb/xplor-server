from rest_framework.utils.encoders import JSONEncoder
from django.contrib.gis.measure import Distance


class CustomJsonEncoderWithDistance(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Distance):
            print(obj)
            return obj.m
        return super(CustomJsonEncoderWithDistance, self).default(obj)
