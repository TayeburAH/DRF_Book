from rest_framework import renderers
import json


class UserRenderer(renderers.JSONRenderer):
    charset = 'utf-8'  # must be used

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = ''

        if 'ErrorDetail' in str(data):
            response = json.dumps({'errors': data})
        else:
            response = json.dumps({'data': data})
        return response
