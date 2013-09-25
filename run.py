from flask import Flask, request, jsonify, render_template
import json
import process

app = Flask(__name__)

@app.route('/', methods = ['POST'])
def index():
	return process.process(request.json)

@app.route('/test', methods = ['GET'])
def test():
    return render_template('test.html')

if __name__ == "__main__":
    app.run(debug = True)
