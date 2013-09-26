from flask import Flask, request, render_template
from process import Process
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/', methods = ['POST'])
def index():
	p = Process()
	return p.process(request.json)

@app.route('/test', methods = ['GET'])
def test():
    return render_template('test.html')

if __name__ == '__main__':
    app.run(debug = True)
