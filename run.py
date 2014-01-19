import sys
from twisted.web.server import Site
from twisted.web.static import File
from twisted.internet.task import LoopingCall

from twisted.python.log import startLogging
from twisted.web.resource import Resource
from autobahn.resource import WebSocketResource

from db import create_db
from process import process
from server import *
from ws_connection import *

from config import *

class post(Resource):
	
	def __init__(self, proc):
		self.p = proc
		Resource.__init__(self)

	def render_GET(self, request):
		return File("./static/index.html").getContent()

	def render_POST(self, request):
		text = request.content.getvalue()
		if LOGGING: 
			log('<<<<'+text)
		resp = self.p.process(text)
		if LOGGING: 
			log('>>>>'+resp)
		request.setHeader('Access-Control-Allow-Origin', '*')
		request.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Requested-With')
		request.setHeader("Content-Type", "application/json")
		return resp

	def render_OPTIONS(self,request):
		request.setHeader('Access-Control-Allow-Origin', '*')
		request.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Requested-With')
		request.setHeader("Content-Type", "application/json")
		return "good" 


if __name__ == '__main__':
#	startLogging(sys.stdout)
#	create_db()
	s = server()	
	p = process(s) 

	factory = ws_factory(p, "ws://0.0.0.0:5000")
	factory.setProtocolOptions(allowHixie76 = True)
	resource = WebSocketResource(factory)

	root = File("./static")
	root.putChild("websocket", resource)
	root.putChild("", post(p))
	site = Site(root, )

	from twisted.internet import reactor
	reactor.listenTCP(5000, site)
	lc = LoopingCall(s.tick)
	lc.start(TICK*0.001)
	reactor.run()

	