from player import *
from game import *
from map import *

class Server:
	def __init__(self):
		self.games = {}
		self.players = {}
		self.map = {}

	def add_game(self, map_id, id):
		self.games[id] = game(self.map[map_id])

	def add_player(self, sid, login, gid):
		game = self.games[gid]
		pl = player(sid, login, game)
		game.join(pl)	
		self.players[sid] = pl
		#for pl in self.games[gid].players:
		#	print login
		#for g in self.games.keys():
		#	print g

	def add_map(self, id, scheme):
		self.map[id] = map(scheme)

	def erase_player(self, sid, gid):
		self.games[gid].leave(sid)
		if len(self.games[gid].players) == 0: del games[gid]

	def clear(self):
		self.games.clear()

	def tick(self):
		for id,g in self.games.iteritems():
			g.tick()
