# -*- coding: utf-8 -*-
from base import *
class StartTestCase(BaseTestCase):
	def test_startTesting(self):
		self.startTesting(True)

	def test_badJson(self):
		resp = self.send(dict = 'notJSON.string.blahblahblah', wo_dumps = True)
		if resp.has_key('message'):
			del resp['message']
		assert resp["result"] == "badJSON", resp
	
	def test_badRequest_not_action(self):
		query =	{
			"params":
			{
				"login": "user",
				"password": "pass"
			}
		}
		resp = self.send(dict = query)
		assert resp["result"] == "badRequest", resp

	def test_badRequest_not_param(self):
		resp = self.send("signin")
		assert resp["result"] == "badRequest", resp

	def test_unknown_action(self):
		resp = self.send("unknown_actionnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn", {"login": "*&&*","password": "pass" })
		if resp.has_key('message'):
			del resp['message']
		assert resp["result"] == "unknownAction", resp
