from flask import Flask, request, render_template, make_response
from process import Process
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/', methods = ['POST'])
def index():
	p = Process(app) 	
	try:
		req = json.loads(request.data)
	except ValueError:
		return p.unknownAction()
	return p.process(req)

@app.route('/', methods = ['OPTIONS'])
def index1():
	pass
	
@app.after_request
def after_request(response):
	response.headers.add('Access-Control-Allow-Origin', '*')
	response.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-Requested-With')
	return response

@app.route('/', methods = ['GET'])
def ws():
	if request.environ.get('wsgi.websocket'):
		ws = request.environ['wsgi.websocket']
		while True:
			message = ws.receive()
			ws.send(message)
	return

if __name__ == '__main__':
    server = WSGIServer(("", 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
    #app.run(debug = True, host='0.0.0.0')
