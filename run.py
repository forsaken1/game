from flask import Flask, request, render_template
from process import Process
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from db import create_db
import json

app = Flask(__name__)

def log(mess):
	open("log_serv", "w").write(mess)

### standart 
@app.route('/', methods = ['POST'])
def index():
	p = Process(app) 
	return p.process(request.data)
	
### for sending tests in browser
@app.route('/test', methods = ['GET'])
def test():
    return render_template('test.html')	

### add header
@app.after_request
def after_request(response):
	response.headers.add('Access-Control-Allow-Origin', '*')
	response.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-Requested-With')
	return response

### sockets
@app.route('/webSocket', methods = ['GET'])
def ws():
	if request.environ.get('wsgi.websocket'):
		ws = request.environ['wsgi.websocket']
		while True:
			message = ws.receive()
			ws.send('server string:' + message)
	return

if __name__ == '__main__':
	create_db()
	server = WSGIServer(("", 5000), app, handler_class=WebSocketHandler)
	server.serve_forever()
	#app.run(debug = True, host='0.0.0.0')
