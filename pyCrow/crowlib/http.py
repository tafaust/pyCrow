#!/usr/bin/python
# -*- coding: utf-8 -*-

"""HTTP Server.
"""

# Python-native imports
import logging.config
from typing import Type
from http.server import BaseHTTPRequestHandler, HTTPServer

# Third-party imports

# App imports


L = logging.getLogger(__name__)
L.debug(f'Loaded module: {__name__}.')


class Server(HTTPServer):
    pykka_traversable = True

    def __init__(self, server_address, handler: Type[BaseHTTPRequestHandler]):
        super().__init__(server_address, handler)
        self._started = False
        L.info('Initialized HTTP Server.')

    def start(self):
        if self._started:
            L.warning('HTTP Server already started. Aborting.')
            return

        try:
            L.info(f'Starting HTTP Server. Listening on {":".join(map(str, self.server_address))}')
            self._started = True
            self.serve_forever()
        except KeyboardInterrupt:
            L.exception('Received keyboard interrupt for the HTTP Server.')
        finally:
            self.server_close()
            L.info('Closed the HTTP Servers socket.')

    def stop(self):
        if self._started:
            self.shutdown()
            self._started = False
            L.info('Gracefully stopped the HTTP Server.')
