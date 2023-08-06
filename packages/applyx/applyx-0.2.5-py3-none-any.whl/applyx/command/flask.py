# coding=utf-8

from applyx.command.base import BaseCommand


class Command(BaseCommand):
    def register(self, subparser):
        parser = subparser.add_parser("flask", help="run flask application")
        parser.add_argument(
            "--host",
            type=str,
            dest="host",
            default="0.0.0.0",
            help="specify server host",
        )
        parser.add_argument(
            "--port",
            type=int,
            dest="port",
            default=8000,
            help="specify server port",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            dest="debug",
            default=False,
            help="enable the Werkzeug debugger",
        )

    def invoke(self, args):
        from applyx.flask.builder import FlaskBuilder, RequestHandler

        flask_app = FlaskBuilder.get_app(self.project, args.debug)
        if flask_app is None:
            return

        flask_app.run(
            host=args.host,
            port=args.port,
            debug=args.debug,
            use_debugger=args.debug,
            use_reloader=args.debug,
            request_handler=RequestHandler,
        )
