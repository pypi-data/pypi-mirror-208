# coding=utf-8

import shortuuid
from loguru import logger
from flask import request, Response, jsonify, abort, has_request_context

from applyx.exception import InternalException


class RequestMiddleware:

    def __init__(self, app, config):
        self.app = app
        self.config = config
        self.uuid = shortuuid.ShortUUID(alphabet="0123456789ABCDEF")

    def setup(self):
        self.app.before_first_request(self.hook_before_first_request)
        self.app.before_request(self.hook_before_request)
        self.app.after_request(self.hook_after_request)
        self.app.register_error_handler(Exception, self.hook_handle_exception)
        self.app.do_teardown_appcontext(self.hook_do_teardown_appcontext)

    def get_remote_address(self):
        environ = request.environ
        remote_host, remote_port = environ["REMOTE_ADDR"], environ["REMOTE_PORT"]
        # local_host, local_port = environ['SERVER_NAME'], environ['SERVER_PORT']

        if request.headers.get("X-Forwarded-For"):
            # HTTP_X_FORWARDED_FOR can be a comma-separated list of IPs.
            # Take just the first one.
            x_forwarded_for = request.headers["X-Forwarded-For"]
            ips = [item.strip() for item in x_forwarded_for.split(",")]
            remote_host = ips.pop(0)
        elif request.headers.get("Remote-Addr"):
            remote_host = request.headers["Remote-Addr"]
        elif request.headers.get("X-Real-IP"):
            remote_host = request.headers["X-Real-IP"]

        if request.headers.get("Remote-Port"):
            remote_port = int(request.headers["Remote-Port"])

        return remote_host, remote_port

    def validate_crossdomain_request(self):
        if not self.config.cors.get('enable'):
            return False
        return True
        # return request.headers.get('Origin', '').endswith(self.config.CORS_WHITELIST_DOMAINS)

    def hook_before_first_request(self):
        pass

    def hook_before_request(self):
        request.id = self.uuid.random(length=4)
        if request.path.startswith("/static"):
            return

        with logger.contextualize(mdc=request.state.id):
            logger.info(f"[uri] {request.method} {request.path}")

            if request.endpoint is not None:
                logger.info(f"[view] {request.endpoint}")

            headers = dict(request.headers)
            if headers:
                logger.debug(f"[headers] {str(headers)}")

            query = request.args.to_dict()
            if query:
                logger.info(f"[query] {str(query)}")

            form = request.form.to_dict()
            if form:
                logger.info(f"[form] {str(form)}")

            if request.data:
                data = request.get_json(silent=True) if request.is_json else request.data.decode()
                logger.info(f"[data] {str(data)}")

            files = request.files.to_dict()
            if files:
                logger.info(f"[files] {str(files)}")

        if request.method == "OPTIONS" and "Access-Control-Request-Method" in request.headers:
            if not self.validate_crossdomain_request():
                return abort(404)

            headers = {
                "CONTENT-TYPE": "text/html",
                "Access-Control-Max-Age": str(self.config.cors.access_control.get('max_age', 60)),
                'Access-Control-Allow-Credentials': str(self.config.cors.access_control.get('allow_credentials', True)),
                "Access-Control-Allow-Origin": request.headers.get("Origin", ""),
                "Access-Control-Allow-Methods": request.headers["Access-Control-Request-Method"],
                "Access-Control-Allow-Headers": request.headers.get("Access-Control-Request-Headers", ""),
            }
            return Response(status=200, headers=headers)

    def hook_after_request(self, response):
        if request.path.startswith("/static"):
            if request.path.endswith(".ejs"):
                response.headers["Content-Type"] = "text/html; charset=utf-8"
            return response

        response.headers["X-Request-Id"] = request.id

        with logger.contextualize(mdc=request.state.id):
            logger.info(f"[http] {response.status_code}")
            if response.is_json:
                logger.info(f"[err] {response.json['err']}")

                if response.json.get("msg"):
                    logger.info(f"[msg] {response.json['msg']}")

                if response.json.get("log"):
                    logger.info(f"[log] {response.json['log']}")

        return response

    def hook_handle_exception(self, error):
        if isinstance(error, HTTPException):
            return error.name, error.code

        if isinstance(error, InternalException):
            return jsonify(err=1, msg=error.msg)

        # generic 500 Internal Server Error
        content = "Internal Server Error"
        logger.exception(content, exc_info=error)

        if self.app.debug:
            content = traceback.format_exc()

        return Response(content, status=500)

    def hook_do_teardown_appcontext(self):
        pass