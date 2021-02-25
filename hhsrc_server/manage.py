#!/usr/bin/env python3
import os
from app import app
from flask_script import Manager, Server

manager = Manager(app)
app.debug = False

server = Server(host="0.0.0.0", port=5000, threaded=True)
manager.add_command("runserver", server)

if __name__ == '__main__':
    manager.run()
