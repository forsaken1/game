from autobahn.websocket import WebSocketServerFactory, WebSocketServerProtocol
import json
from config import *

class ws_factory(WebSocketServerFactory):
	def __init__(self, proc, url = None, debug=False, debugCodePaths=False):
		self.protocol = ws_connection
		self.process = proc
		WebSocketServerFactory.__init__(self, url = url, debug = debug, debugCodePaths = debugCodePaths)


class ws_connection(WebSocketServerProtocol):
	def onConnect(self, req):
		print 'connect'
		self.player = None
		return WebSocketServerProtocol.onConnect(self, req)

	def onMessage(self, msg, binary):
		if LOGGING:
			log(msg)
		msg = json.loads(msg)
		if self.player is None:
			self.factory.process.valid.get_id(msg['params']['sid'])
			pid = self.factory.process.valid.get_id(msg['params']['sid'])
			self.player = self.factory.process.server.players[pid]
			self.player.connects.append(self)
		self.player.action(msg)