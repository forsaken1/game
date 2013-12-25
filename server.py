from player import *
from game import *
from map import *
from config import *

class server:
	def __init__(self):
		print 'start'
		self.games, self.players, self.maps = {}, {}, {}
		self.sync_mode = False

	def equal(self, x, y):
		return abs(x-y) < EPS

	def add_game(self, map_id, id, accel, friction, gravity, MaxVelocity):
		self.games[id] = game(self.maps[map_id], self, accel, friction, gravity, MaxVelocity)

	def add_player(self, pid, login, gid):
		game = self.games[gid]
		pl = player(pid, login, game, self)
		game.join(pl)	
		self.players[pid] = pl

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
