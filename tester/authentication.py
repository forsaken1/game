# -*- coding: utf-8 -*-
from base import *
class AuthTestCase(BaseTestCase):

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

	def test_signup_ok(self):
		self.signup_user()

	def test_signup_bad_pass(self):
		resp = self.send("signup",{"login": self.default('user'),"password": "p"})
		assert resp["result"] == "badPassword", resp

	def test_signup_badRequest(self):
		resp = self.send("signup",{"login": self.default('user')})
		assert resp["result"] == "badRequest", resp

	def test_signup_bad_tooshort(self):
		resp = self.send("signup",{"login": "u","password": "pass3"})
		assert resp["result"] == "badLogin", resp

	def test_signup_bad_toolong(self):
		resp = self.send("signup",{"login": "ThisStringConsistMoreThen40LattersNeedSomeMore", "password": "pass3"})
		assert resp["result"] == "badLogin", resp
		
	def test_signup_already_exists(self):
		self.signup_user()
		resp = self.send("signup", {"login": self.default('user', 1), "password": "pass"})
		assert resp["result"] == "userExists", resp

	def test_signin_ok(self):
		self.signin_user()

	def test_signin_bad_combi(self):
		self.signup_user()
		resp = self.send("signin",{"login": self.default('user', 1), "password": "bad_pass"})
		assert resp["result"] == "incorrect", resp

	def test_signout_ok(self):
		sid = self.signin_user()
		resp = self.send("signout", {"sid": sid})
		assert resp["result"] == "ok", resp

	def test_signout_bad_sid(self):
		self.startTesting()
		sid1 = self.signin_user()
		sid2 = self.signin_user()
		resp = self.send("signout", {"sid": sid1 + sid2})
		assert resp["result"] == "badSid", resp

	def test_getGameParams_bad_sid(self):
		self.startTesting()
		sid1 = self.signin_user()
		sid2 = self.signin_user()
		resp = self.send("getGameParams", {"sid": sid1 + sid2})
		assert resp["result"] == "badSid", resp

	def test_getGameParams_not_in_game(self):
		sid = self.signin_user()
		resp = self.send("getGameParams", {"sid": sid})
		assert resp["result"] == "notInGame", resp
