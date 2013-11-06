import os

from flask import Flask

app = Flask(__name__)
app.debug = True

def start(environ, start_response):  
	path = environ["PATH_INFO"]
	return app(environ, start_response)  

import routes