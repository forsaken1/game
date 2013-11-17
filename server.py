from player import *
from game import *
from map import *

class server:
	def __init__(self, tick, eps):
		print 'start'
		self.ACCEL = 0.02
		self.tick_size, self.eps = tick, eps
		self.games, self.players, self.maps = {}, {}, {}
		self.sync_mode = False

	def equal(self, x, y):
		return abs(x-y) < self.eps

	def add_game(self, map_id, id):
		self.games[id] = game(self.maps[map_id], self)

	def add_player(self, pid, login, gid):
		game = self.games[gid]
		pl = player(pid, login, game, self)
		game.join(pl)	
		self.players[pid] = pl
		#for pl in self.games[gid].players:
		#	print login
		#for g in self.games.keys():
		#	print g

	def add_map(self, id, scheme):
		self.maps[id] = map(scheme, self)

	def erase_player(self, sid, gid):
		self.games[gid].leave(sid)
		if len(self.games[gid].players) == 0: del games[gid]

	def clear(self, new_mode):
		self.games.clear()
		self.players.clear()
		self.maps.clear()
		self.sync_mode = True if new_mode == 'sync' else False

	def tick(self):
		if not self.sync_mode:
			for id,g in self.games.iteritems():
				g.tick()
