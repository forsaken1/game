from autobahn.websocket import WebSocketServerFactory, WebSocketServerProtocol
import json
from config import *

class ws_factory(WebSocketServerFactory):
	def __init__(self, proc, url = None, debug=True, debugCodePaths=True):
		self.protocol = ws_connection
		self.setSessionParameters()

		self.process = proc
		WebSocketServerFactory.__init__(self, url = url, debug = debug, debugCodePaths = debugCodePaths)


class ws_connection(WebSocketServerProtocol):
	def onConnect(self, req):
		print 'connect'
		self.player = None
		return WebSocketServerProtocol.onConnect(self, req)
#del conect onClose
	def onMessage(self, msg, binary):
	#	print 'END'
		msg = json.loads(msg)
		if self.player is None:
			pid = self.factory.process.valid.get_pid(msg['params']['sid'])
			self.player = self.factory.process.server.players[pid]
			self.player.connects.append(self)
		self.player.action(msg)

	def onClose(self, wasClean, code, reason):
		print 'close'
		if PHILIPP and self.player:
			self.player.respawn = 1
		if self.player:
			self.player.connects.remove(self)
		return WebSocketServerProtocol.onClose(self, wasClean, code, reason)