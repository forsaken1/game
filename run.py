import sys
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File
from twisted.internet.task import LoopingCall

from twisted.web.resource import Resource
from autobahn.resource import WebSocketResource

from db import create_db
from process import process
from server import *
from ws_connection import *

TICK, EPS = 30, 1e-6

class post(Resource):
	
	def __init__(self, proc):
		self.p = proc
		Resource.__init__(self)

	def render_GET(self, request):
		return File("conf")

	def render_POST(self, request):
		text = request.content.getvalue()
		resp = self.p.process(text)
		request.setHeader('Access-Control-Allow-Origin', '*')
		request.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Requested-With')
		request.setHeader("Content-Type", "application/json")
		print resp
		return resp

	def render_OPTIONS(self,request):
		request.setHeader('Access-Control-Allow-Origin', '*')
		request.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Requested-With')
		request.setHeader("Content-Type", "application/json")
		return "good" 

if __name__ == '__main__':
	create_db()
	s = server(TICK, EPS)
	p = process(s) 

	if len(sys.argv) > 1 and sys.argv[1] == 'debug':
		log.startLogging(sys.stdout)
		debug = True
	else:
		debug = False

	factory = ws_factory(p, "ws://localhost:5000", debug = debug, debugCodePaths = debug)
	resource = WebSocketResource(factory)

	root = File(".")
	root.putChild("websocket", resource)
	root.putChild("conf", File("conf"))
	root.putChild("", post(p))
	site = Site(root)

	from twisted.internet import reactor
	reactor.listenTCP(5000, site)
	lc = LoopingCall(s.tick)
	lc.start(0.03)
	reactor.run()