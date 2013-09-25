from flask import Flask, request, jsonify

app = Flask(__name__)
 
html_page = """<!DOCTYPE HTML>
<input type = button value = "Press" onclick = "send()">
<script src = "http://code.jquery.com/jquery-1.10.2.min.js"></script>
<script>
function send()
{
 $.ajax({
  type: 'POST',
  data: '{"request":"21"}',
  contentType: "application/json; charset=utf-8",
  url: 'http://localhost:5000',
  dataType: "json",
  success: function(data)
  {
   alert(data.message);
  },
 });
}
</script>
"""

import json
import process

@app.route('/', methods = ['POST'])
def index():
    #return jsonify(request.json['request'])
	return process()

@app.route('/test', methods = ['GET'])
def test():
    return html_page

if __name__ == "__main__":
    app.run(debug = True)
