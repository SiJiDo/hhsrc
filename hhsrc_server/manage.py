#!/usr/bin/env python3
import os
from app import app
from flask_script import Manager, Server
from geventwebsocket.handler import WebSocketHandler
from gevent import pywsgi

manager = Manager(app)
app.debug = False

# server = Server(host="0.0.0.0", port=5000, threaded=True)
server = pywsgi.WSGIServer(('0.0.0.0', 5000), app, handler_class=WebSocketHandler)
server.serve_forever()
manager.add_command("runserver", server)


if __name__ == '__main__':
    manager.run()
