# coding=utf-8

import os
import logging
import traceback
from importlib import import_module
from logging.handlers import RotatingFileHandler

from loguru import logger
from addict import Dict
from flask import Flask
from flask_compress import Compress
from werkzeug.routing import BaseConverter
from werkzeug.exceptions import HTTPException
from werkzeug.serving import WSGIRequestHandler
from jinja2 import FileSystemLoader

from applyx.conf import settings
from applyx.flask.views import ViewWrapper
from applyx.flask.middlewares import RequestMiddleware
from applyx.jinja2 import FILTERS, TESTS
from applyx.utils import get_log_dir


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *args):
        super().__init__(url_map)
        self.regex = args[0]


class RequestHandler(WSGIRequestHandler):
    def log(self, type, message, *args):
        content = "%s [%s] %s" % (
            self.address_string(),
            self.log_date_time_string(),
            message % args,
        )
        logger = logging.getLogger("werkzeug")
        getattr(logger, type)(content)


class FlaskBuilder:
    @classmethod
    def get_app(cls, project, debug=False):
        module_path = f"{project.__package__}.api.flask"
        try:
            module = import_module(module_path)
        except ModuleNotFoundError:
            builder_cls = cls
        else:
            builder_cls = getattr(module, "Builder", None)
            if builder_cls is None or not issubclass(builder_cls, cls):
                print(f"invalid flask build path {module_path}.Builder")
                return None

        builder = builder_cls(project, debug)
        builder.make()
        return builder.app

    def __init__(self, project=None, debug=False):
        self.project = project
        self.debug = debug
        self.api_dir = os.path.join(project.__path__[0], "api")
        self.config = Dict()
        self.app = None

    def make(self):
        self.init_config()
        self.init_logging()

        flask_kwargs = {}
        if self.config.get('static_dir'):
            path = os.path.realpath(os.path.join(settings.get('project.workspace'), self.project.__name__, self.config.static_dir))
            if not os.path.exists(path):
                raise Exception(f"static path {path} not exists")
            flask_kwargs.update({"static_folder": path, "static_url_path": "/static"})

        self.app = Flask(settings.get('project.name'), **flask_kwargs)
        self.mapping_config()

        if self.config.gzip.get('enable'):
            compress = Compress()
            compress.init_app(self.app)

        self.app.url_map.converters["regex"] = RegexConverter

        self.setup_routes()
        self.setup_session()
        self.setup_jinja2()

        middleware = RequestMiddleware(self.app, self.config)
        middleware.setup()

        if self.debug:
            logger.warning("Debug mode is on.")

        return self.app

    def init_config(self):
        self.config = settings.get('flask')

    def init_logging(self):
        sink = RotatingFileHandler(
            filename=os.path.join(get_log_dir(), "web.log"),
            maxBytes=settings.get('logging.handlers.file.rotate.max_bytes'),
            backupCount=settings.get('logging.handlers.file.rotate.backup_count'),
            encoding="utf8",
        )
        logging_level = logging.DEBUG if self.debug else settings.get('logging.level')
        logging_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level}</level> | "
            "<cyan>({process},{thread})</cyan> "
            "[{extra[mdc]}] - {message}"
        )

        logger.remove()
        logger.configure(extra={"mdc": "x"})
        logger.add(sink=sys.stderr, level=logging_level, format=logging_format)
        logger.add(sink=sink, level=logging_level, format=logging_format)

    def mapping_config(self):
        # TODO: convert config attributes into uppercase
        self.app.config.from_mapping(dict(self.config.items()))

    def setup_routes(self):
        base_path = os.path.join(self.api_dir, "views")
        for dirpath, _, filenames in os.walk(base_path):
            for filename in filenames:
                full_pathname = os.path.join(dirpath, filename)
                if filename.startswith("_") or not filename.endswith(".py"):
                    continue
                package_dir = os.path.abspath(os.path.join(self.project.__path__[0], os.pardir))
                module_path = full_pathname[len(package_dir) + 1: -len(".py")].replace(os.sep, ".")
                module = import_module(module_path)
                for key in dir(module):
                    if key.startswith("_"):
                        continue
                    value = getattr(module, key)
                    if not isinstance(value, ViewWrapper):
                        continue
                    relative_path = full_pathname[len(base_path) + 1 : -len(".py")].replace(os.sep, ".")
                    name = f"views.{relative_path}.{key}"
                    view_func = value(name)
                    self.app.add_url_rule(value.route, view_func=view_func)

    def setup_session(self):
        if not self.config.session.get('enable'):
            return
        if settings.get('redis') and self.config.session.get('redis_alias') in settings.get('redis'):
            import flask_session
            from applyx.redis import RedisManager

            session_redis = RedisManager.instance().get(self.config.session.redis_alias)
            if session_redis:
                self.app.config.SESSION_REDIS = session_redis
                flask_session.Session().init_app(self.app)

    def setup_jinja2(self):
        path = os.path.join(self.api_dir, self.config.get('template_dir'))
        if not os.path.exists(path):
            return

        self.app.jinja_loader = FileSystemLoader(path)
        env = self.app.jinja_env
        env.filters.update(FILTERS)
        env.tests.update(TESTS)
        env.globals.update({"WEB": settings.get('web')})
