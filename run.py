from flask import Flask, request, render_template
from process import Process

app = Flask(__name__)

@app.route('/', methods = ['POST'])
def index():
	p = Process(app)
	return p.process(request.json)
	
@app.after_request
def after_request(response):
	response.headers.add('Access-Control-Allow-Origin', '*')
	response.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-Requested-With')
	return response

@app.route('/test', methods = ['GET'])
def test():
    return render_template('test.html')

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0')
