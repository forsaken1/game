from flask import request, render_template
from app import app
from process import Process
from websocket import WebSocket

def log(mess):
	open("log_serv", "w").write(mess)

### add headers
@app.after_request
def after_request(response):
	response.headers.add('Access-Control-Allow-Origin', '*')
	response.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-Requested-With')
	return response

### sockets
@app.route('/websocket', methods = ['GET'])
def ws():
	if request.environ.get('wsgi.websocket'):
		ws = request.environ['wsgi.websocket']
		ws_proc = WebSocket()
		while True:
			message = ws.receive()
			ws.send(ws_proc.get(message))

### client routes
@app.route('/', methods = ['POST'])
def post():
	p = Process(app)
	return p.process(request.data)

@app.route('/', methods = ['GET'])
def index():
	return render_template('index.html')
