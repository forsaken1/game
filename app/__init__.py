import os

from flask import Flask

app = Flask(__name__, template_folder='static')
app.debug = True

def start(environ, start_response):
	return app(environ, start_response)  

import routes