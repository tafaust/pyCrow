#!/usr/bin/python
# -*- coding: utf-8 -*-

"""REST Actor.
"""

# Python-native imports
import logging.config
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading

# Third-party imports
import pykka

# App imports
from pyCrow.crowlib.aux import Action


# prepare logging, i.e. load config and get the root L
L = logging.getLogger()


class RestActor(pykka.ThreadingActor):
    def __init__(self, config: dict):
        super().__init__()
        self._config = config
        self._server = Server((self._config.get('address', ''), self._config.get('port', 1337)))
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
            self._server = Server((self._config.get('address', ''), self._config.get('port', 1337)))
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

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        _headers = str(self.headers).replace('\n\n', '').replace('\n', ', ')
        L.debug(f'Method: [GET], Path: [{self.path}], Headers: [{_headers}]')
        self._set_response()
        pykka.ActorRegistry.get_by_class_name('AppActor')[0].ask({})
        # self.wfile.write(f'GET request for {self.path}'.encode('utf-8'))

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
        pykka.ActorRegistry.get_by_class_name(msg.pop('target', 'AppActor'))[0].tell(msg)
        self._set_response()
        # self.wfile.write(f'POST request for {self.path}'.encode('utf-8'))


# Server
class Server(HTTPServer):
    pykka_traversable = True

    def __init__(self, server_address):
        super().__init__(server_address, RESTRequestHandler)
        self._started = False
        L.info('Initialized REST Server.')

    def start(self):
        if self._started:
            L.warning('REST Server already started. Aborting.')
            return

        try:
            L.info('Starting REST Server.')
            self._started = True
            self.serve_forever()
        except KeyboardInterrupt:
            L.exception('Received keyboard interrupt for the Server.')
        finally:
            self.server_close()
            L.info('Closed the REST Servers socket.')

    def stop(self):
        if self._started:
            self.shutdown()
            self._started = False
            L.info('Gracefully stopped the REST Server.')
