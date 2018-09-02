from __future__ import unicode_literals

import json
import os

import falcon
from dragnn_wrapper import SyntaxNet

language = os.environ.get('LANGUAGE', 'English')
syntaxnet = SyntaxNet(lang=language, model_dir="/usr/local/tfmodels/")


class SyntaxNetResource:
    def on_post(self, request, response):
        text = request.get_param("data")

        if text and text != "":
            data = syntaxnet.parse(text)
        else:
            data = {"error": "This API requires some text sent as request data."}

        response.set_header("X-LANGUAGE", language)
        response.media = data
        response.content_type = falcon.MEDIA_JSON


app = falcon.API()
app.req_options.auto_parse_form_urlencoded = True
app.add_route('/', SyntaxNetResource())
