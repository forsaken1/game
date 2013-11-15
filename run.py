from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

from app import start, db

if __name__ == '__main__':
	db.create_db()
	http_server = WSGIServer(('', 5000), start, handler_class=WebSocketHandler)
	http_server.serve_forever()