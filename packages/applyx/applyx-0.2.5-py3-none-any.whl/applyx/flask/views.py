# coding=utf-8

import re
import requests
from flask import request
from flask import jsonify
from flask import Response
from flask import abort
from flask import stream_with_context
from flask.views import MethodView
from flask_inputs import Inputs
from flask_inputs.validators import JsonSchema

from applyx.service import KongService


class BaseView(MethodView):
    route = ""
    access_denied = False
    schema = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # https://pythonhosted.org/Flask-Inputs/
        # https://json-schema.org/understanding-json-schema/reference/index.html
        if self.schema:
            self._post_inputs_cls = type(
                "JsonInputs", (Inputs,), dict(json=[JsonSchema(schema=self.schema)])
            )

    def is_mobile(self):
        agent = request.user_agent.string
        features = [
            "android",
            "iphone",
            "ipad",
            "ipod",
            "windows phone",
            "symbian",
            "blackberry",
        ]
        matcher = re.search("|".join(features), agent, re.I)
        return True if matcher else False

    def is_weixin(self):
        agent = request.user_agent.string
        matcher = re.search("micromessenger", agent, re.I)
        return True if matcher else False

    def dispatch_request(self, *args, **kwargs):
        if self.access_denied:
            return abort(404)

        if self.schema and request.method == "POST":
            inputs = self._post_inputs_cls(request)
            if not inputs.validate():
                return jsonify(err=1, msg="参数错误", log=inputs.errors.pop())

        return super().dispatch_request(*args, **kwargs)


class ProxyView(BaseView):
    target = {
        "url": "",
        "kwargs": {
            "params": None,
            "data": None,
            "json": None,
            "files": None,
            "headers": None,
            "cookies": None,
            "auth": None,
        }
    }

    def get(self, *args, **kwargs):
        self.target["kwargs"]["params"] = request.args.to_dict()
        self.target["kwargs"]["headers"] = dict(request.headers)
        return self._make_request()

    def post(self, *args, **kwargs):
        self.target["kwargs"]["params"] = request.args.to_dict()
        self.target["kwargs"]["headers"] = dict(request.headers)
        self.target["kwargs"]["json"] = request.get_json(silent=True) or {}
        return self._make_request()

    def put(self, *args, **kwargs):
        self.target["kwargs"]["params"] = request.args.to_dict()
        self.target["kwargs"]["headers"] = dict(request.headers)
        self.target["kwargs"]["json"] = request.get_json(silent=True) or {}
        return self._make_request()

    def delete(self, *args, **kwargs):
        self.target["kwargs"]["params"] = request.args.to_dict()
        self.target["kwargs"]["headers"] = dict(request.headers)
        return self._make_request()

    def before_request(self):
        # self.target["url"] = ""
        raise NotImplementedError

    def before_response(self, response):
        pass

    def _make_request(self, **kwargs):
        self.before_request()
        response = requests.request(request.method, self.target["url"], **self.target["kwargs"], stream=True)
        self.before_response(response)
        return Response(stream_with_context(response.iter_content(chunk_size=2048)), headers=response.headers)


class ViewWrapper:
    route = None

    def __init__(self, view_class):
        self.view_class = view_class

    def __call__(self, name):
        view = self.view_class.as_view(name)
        view.route = self.route
        return view


def url(route):
    return type("_Wrapper", (ViewWrapper,), { "route": route })
