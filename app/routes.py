from flask import request, render_template
from app import app
from process import Process

def log(mess):
	open("log_serv", "w").write(mess)

### add headers
@app.after_request
def after_request(response):
	response.headers.add('Access-Control-Allow-Origin', '*')
	response.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-Requested-With')
	return response

### standart 
@app.route('/', methods = ['POST'])
def index():
	p = Process(app) 
	return p.process(request.data)
	
### for sending tests in browser
@app.route('/', methods = ['GET'])
def test():
	return render_template('test.html')	

### sockets
@app.route('/websocket', methods = ['GET'])
def ws():
	if request.environ.get('wsgi.websocket'):
		ws = request.environ['wsgi.websocket']
		while True:
			message = ws.receive()
			ws.send('server string:' + message)