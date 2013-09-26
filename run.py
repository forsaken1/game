from flask import Flask, request, render_template
from process import Process
import re

app = Flask(__name__)

@app.route('/', methods = ['POST'])
def index():
	p = Process()
	return p.process(request.json)

@app.route('/test', methods = ['GET'])
def test():
    return render_template('test.html')

@app.route('/foo', methods = ['GET'])
def foo():
	reg_exp = re.compile('\w{4,40}', re.IGNORECASE)
	answer = reg_exp.match('qwe1')
	if answer:
		return '123'
	else:
		return '321'

if __name__ == '__main__':
    app.run(debug = True)
