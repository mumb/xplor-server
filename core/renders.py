from rest_framework.renderers import JSONRenderer
from .encoders import CustomJsonEncoderWithDistance


class CustomJsonRenderer(JSONRenderer):
    encoder_class = CustomJsonEncoderWithDistance
