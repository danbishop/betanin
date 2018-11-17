#!/usr/bin/env python3

from gevent import monkey; monkey.patch_all()

# python
import sys
import signal

# 3rd party
import gevent
from flask import Flask

# betanin
from betanin import api
from betanin import client
from betanin.api import jobs
from betanin.config import Config
from betanin.api.jobs import import_torrents
from betanin.extensions import db
from betanin.extensions import cors
from betanin.extensions import rest
from betanin.extensions import migrate
from betanin.extensions import socketio


def stop(sig_num, frame):
    print('shutting down')
    sys.exit(0)


def create_app():
    app = Flask(__name__.split('.')[0])
    app.url_map.strict_slashes = False
    app.config.from_object(Config)
    register_extensions(app)
    register_blueprints(app)
    return app


def register_extensions(app):
    # orm
    db.init_app(app)
    # cors
    cors.init_app(app)
    from sqlalchemy_utils import force_instant_defaults
    force_instant_defaults()
    # migrations
    from betanin.api.orm.models.torrent import Torrent
    from betanin.api.orm.models.line import Line
    migrate.init_app(app, db)
    # socketio
    socketio.init_app(app)


def register_blueprints(app):
    # blueprint extensions (before register)
    rest.init_app(api.blueprint)
    _origins = app.config.get('CORS_ORIGIN_WHITELIST', '*')
    cors.init_app(api.blueprint, origins=_origins)
    cors.init_app(client.blueprint, origins=_origins)
    # blueprints
    app.register_blueprint(client.blueprint)
    app.register_blueprint(api.blueprint)


if __name__ == "__main__":
    # setup stop
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    # setup
    from gevent.pywsgi import WSGIServer
    flask_app = create_app()
    def _make_starter(module):
        def _context_wrapper():
            with flask_app.app_context():
                module.start()
        return _context_wrapper
    # jobs
    port = 5000
    _http_server = WSGIServer(('', port), log=None, application=flask_app)
    # hello
    print(f'starting on port {port}')
    # start http job and extra jobs
    gevent.joinall((
        socketio.start_background_task(_make_starter(import_torrents)),
        socketio.start_background_task(_http_server.start),
    ))
