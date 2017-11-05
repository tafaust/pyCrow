#!/usr/bin/python
# -*- coding: utf-8 -*-

"""REST Actor.
"""

import json
# Python-native imports
import logging.config
import threading
from http.server import BaseHTTPRequestHandler

# Third-party imports
import pykka

# App imports
from pyCrow.crowlib.aux import Action
from pyCrow.crowlib.http import Server

L = logging.getLogger(__name__)
L.debug(f'Loaded module: {__name__}.')


class RestActor(pykka.ThreadingActor):
    def __init__(self, config: dict):
        super().__init__()
        self._config = config
        self._server = Server((self._config.get('address', ''), self._config.get('port', 34566)),
                              handler=RESTRequestHandler)
        self._server_thread = None

    def on_start(self):
        L.info(msg=f'Started RestActor ({self.actor_urn})')
        self._server_thread = threading.Thread(target=self._server.start, daemon=False)
        self._server_thread.start()

    def on_stop(self):
        L.info('RestActor is stopped.')

    def on_failure(self, exception_type, exception_value, traceback):
        L.error(f'RestActor failed: {exception_type} {exception_value} {traceback}')

    def on_receive(self, msg: dict):
        L.info(msg=f'RestActor received message: {msg}')
        # process msg and alter state accordingly
        _cmd = msg.get('cmd', '').lower()
        # introduce actions to modify this actors state, i.e. do alterations to the web server
        if _cmd == Action.SERVER_START.get('cmd'):
            self._server.start()
        elif _cmd == Action.SERVER_RESTART.get('cmd'):
            self._server.stop()
            L.info('Creating new HTTP Server instance.')
            self._server = Server(
                (self._config.get('address', ''), self._config.get('port', 34566)),
                handler=RESTRequestHandler)
            self._server_thread = threading.Thread(target=self._server.start, daemon=False)
            self._server_thread.start()
        elif _cmd == Action.SERVER_STOP.get('cmd'):
            self._server.stop()
            self._server_thread.join()
        else:
            # default: do nothing but log this event
            L.info(msg=f'Received message {msg} which cannot be processed.')


# RESTRequestHandler
class RESTRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def _set_response(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        _headers = str(self.headers).replace('\n\n', '').replace('\n', ', ')
        L.debug(f'Method: [GET], Path: [{self.path}], Headers: [{_headers}]')
        response = f'GET request for {self.path} has no implementation'
        L.warning(response)
        # pykka.ActorRegistry.get_by_class_name('AppActor')[0].ask({})
        self._set_response()
        self.wfile.write(json.dumps({'error': response}).encode('utf-8'))

    def do_POST(self):
        # size of data
        content_length = int(self.headers['Content-Length'])
        # POST data itself
        post_data = self.rfile.read(content_length)
        _headers = str(self.headers).replace('\n\n', '').replace('\n', ', ')
        L.debug(f'Method: [POST], Path: [{self.path}], Headers: [{_headers}], '
                f'Body: [{post_data.decode("utf-8")}]')

        # todo validate msg
        msg: dict = json.loads(post_data.decode('utf-8'))
        # fixme check if there is such an actor, send an appropriate REST response?
        try:
            pykka.ActorRegistry.get_by_class_name(msg.get('target', 'AppActor'))[0].tell(msg)
            self._set_response()
            self.wfile.write(str({'error': ''}).encode('utf-8'))
        except IndexError:
            response = f'There is no such target actor {msg.get("target", "appActor")} registered.'
            L.warning(response)
            pykka.ActorRegistry.get_by_class_name('AppActor')[0].tell(msg)
            self._set_response(404)
            self.wfile.write(json.dumps({'error': response}).encode('utf-8'))
