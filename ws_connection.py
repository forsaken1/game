from autobahn.websocket import WebSocketServerFactory, WebSocketServerProtocol
import json

class ws_factory(WebSocketServerFactory):
	def __init__(self, games, url = None, debug=False, debugCodePaths=False):
		self.protocol = ws_connection
		self.games = games
		WebSocketServerFactory.__init__(self, url = url, debug = debug, debugCodePaths = debugCodePaths)


class ws_connection(WebSocketServerProtocol):
	def onConnect(self, req):
		print 'connect'
		self.player = None
		return WebSocketServerProtocol.onConnect(self, req)

	def onMessage(self, msg, binary):
		msg = json.loads(msg)
		if self.player is None: 
			self.player = self.factory.games.players[msg['params']['sid']]
			self.player.connects.append(self)
		self.player.action(msg)