from sympy.geometry import *
from player import *
import json
from datetime import datetime

class all_games:
	def __init__(self):
		self.games = {}
		self.players = {}

	def add_game(self, map, id):
		self.games[id] = game(map)

	def add_player(self, sid, login, gid):
		game = self.games[gid]
		pl = player(sid, login, game)
		game.join(pl)	
		self.players[sid] = pl
		#for pl in self.games[gid].players:
		#	print login
		#for g in self.games.keys():
		#	print g

	def erase_player(self, sid, gid):
		self.games[gid].leave(sid)
		if len(self.games[gid].players) == 0: del games[gid]

	def clear(self):
		self.games.clear()

	def tick(self):
		for id,g in self.games.iteritems():
			g.tick()

class game:

	def __init__(self, map):
		self.height = len(map)
		self.width = len(map[0])
		self.map = map

		self.mess = ''
		self.pl_mess = []
		self.pr_mess = []

		self.ticks = 0
		self.players = []
		self.projects = []
		
		self.spawns = []
		self.items = []
		for i in range(self.height):
			for j in range(self.width):
				dot = self.map[i][j]
				if dot == '$': self.spawns.append(Point(j, i))
				if 'A' <= dot <= 'Z': self.items.append(0)

	def join(self, player):
		self.players.append(player)

	def leave(self, sid):
		for pl in self.players:
			if pl.sid == sid: del pl
	
	def set_mess(self):
		self.mess = json.dumps({
			'tick': self.ticks,
			'players': self.pl_mess,
			'projectiles': self.pr_mess,
			'items': self.items
		})

	def tick(self):
		self.ticks += 1

		self.pl_mess = []
		self.pr_mess = []
		#for p in project
		#
		for p in self.players:
			p.tick()
		for i in self.items:
			i -= TICK
		self.set_mess()

		for p in self.players:
			p.write_mess()