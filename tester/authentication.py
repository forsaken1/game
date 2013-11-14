# -*- coding: utf-8 -*-
from base import *
class AuthTestCase(BaseTestCase):
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

	def test_getGameParam_bad_sid(self):
		self.startTesting()
		sid1 = self.signin_user()
		sid2 = self.signin_user()
		resp = self.send("getGameParam", {"sid": sid1 + sid2})
		assert resp["result"] == "badSid", resp

	def test_getGameParam_not_in_game(self):
		sid = self.signin_user()
		resp = self.send("getGameParam", {"sid": sid})
		assert resp["result"] == "notInGame", resp
