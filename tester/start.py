# -*- coding: utf-8 -*-
from base import *
class StartTestCase(BaseTestCase):

	def test_getGameParam_ok(self):
		sid = self.join_game()
		resp = self.send("getGameParams", {"sid": sid})
		assert resp['result'] == 'ok' and resp.has_key('tickSize') and resp.has_key('accuracy'), resp
		BaseTestCase.tickSize, BaseTestCase.accuracy = resp['tickSize'], resp['accuracy']

	def test_startTesting(self):
		self.startTesting(True)

