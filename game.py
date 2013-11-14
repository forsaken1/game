from sympy.geometry import *
from player import *
import json
from datetime import datetime


class game:

	def __init__(self, map, server):
		self.map, self.server = map, server
		self.cur_spawn = 0
		self.c_spawns, c_items = map.get_attr()
		self.items = [0]*c_items
		self.mess = ''
		self.pl_mess = pr_mess = []

		self.c_ticks = 0
		self.players = []
		self.projects = []
		

	def join(self, player):
		self.players.append(player)

	def leave(self, sid):
		for pl in self.players:
			if pl.sid == sid: del pl

	def set_mess(self):
		self.mess = json.dumps({
			'tick': self.c_ticks,
			'players': self.pl_mess,
			'projectiles': self.pr_mess,
			'items': self.items
		})

	def get_spawn(self):
		ret = self.map.spawns[self.cur_spawn]
		self.cur_spawn +=1
		self.cur_spawn %= self.c_spawns
		return ret	

	def tick(self):
		self.c_ticks += 1

		self.pl_mess = []
		self.pr_mess = []
		#for p in project
		#
		for p in self.players:
			p.tick()
		for i in self.items:
			i -= self.server.tick_size
		self.set_mess()
		print self.pl_mess
		for p in self.players:
			p.write_mess()

	def sync_tick(self):
		if self.server.sync_mode:
			if all(p.was_action for p in self.players):
				for p in self.players:
					p.was_action = False
				self.tick()