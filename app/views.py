from app import app, process
from flask import request

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		return 'kgjh'
	else:
		return 'Bad request'

@app.route('/test', methods=['POST'])
def test():
	return jsonify({"message": "0"})