# -*- coding: utf-8 -*-

from base import *
import time

class ChatTestCase(BaseTestCase):

	def test_sendMessage_ok(self):
		self.send_message()



	def test_sendMessage_ok_from_game(self):
		gid = self.get_game()
		sid = self.signin_user()
		self.join_game(gid, sid)
		self.send_message(sid, game = gid, text = "***")		
	
	def test_sendMessage_badSid(self):
		self.startTesting()
		sid1 = self.signin_user()
		sid2 = self.signin_user()
		resp = self.send("sendMessage", {"sid": sid1 + sid2,"game": "","text": "hello"})
		assert resp["result"] == "badSid", resp

	def test_sendMessage_badGame(self):
		self.startTesting()
		sid = self.signin_user()		
		resp = self.send("sendMessage", {"sid": sid,"game": 1111,"text": "hello"})	
		assert resp["result"] == "badGame", resp

	def test_sendMessage_badGame_another_game(self):
		self.startTesting()
		sid = self.signin_user()
		gid = self.get_game()
		self.join_game(gid, sid)
		resp = self.send("sendMessage", {"sid": sid,"game": "","text": "hello"})	
		assert resp["result"] == "badGame", resp

	def test_getMessages_ok(self):
		sid1 = self.signin_user()
		self.send_message(text = "0th")
		resp = self.send("getMessages",
			{
				"sid": sid1,
				"game": "",
				"since": 0
			})
		assert resp.has_key('messages'), resp
		max_time = 0
		for mess in resp['messages']:
			assert mess.has_key('text') and mess.has_key('login') and mess.has_key('time'), mess
			if mess['time'] > max_time: max_time = mess['time']
		
		time.sleep(2)
		sid1 = self.send_message(text = "1st")
		time.sleep(2)
		sid2 =self.send_message(text = "2nd")
		
		resp = self.send("getMessages",
			{
				"sid": sid1,
				"game": "",
				"since": max_time + 1
			})
		
		assert resp.has_key('messages'), resp
		messages = resp['messages']
		assert len(messages) == 2, resp
		for mess in messages:
			assert mess.has_key('text') and mess.has_key('login') and mess.has_key('time'), mess	
			del mess['time']
			assert mess['text'] in {'1st', '2nd'}
			assert mess['login'] in {self.default('user', 2), self.default('user', 1)}
	
	def test_getMessages_from_game_ok(self):
		[id1, sid1] = self.get_game(sid_returned = True)
		[id2, sid2] = self.get_game(sid_returned = True)
		self.join_game
		self.send_message(sid = sid1, text = "0th", game = id1)
		time.sleep(2)
		timestamp1 = int(time.time())
		sid1 =self.send_message(sid = sid1, text = "1st", game = id1)
		time.sleep(2)
		sid2 =self.send_message(sid = sid2, text = "2nd", game = id2)
		time.sleep(2)
		sid3 =self.send_message(sid = sid1, text = "3rd", game = id1)
		resp = self.send("getMessages",
			{
				"sid": sid1,
				"game": id1,
				"since": timestamp1
			})
		assert resp.has_key('messages'), resp
		messages = resp['messages']
		assert len(messages) == 2, resp
		for mess in messages:
			assert mess.has_key('text') and mess.has_key('login') and mess.has_key('time'), mess	
			del mess['time']
			assert mess['text'] in {'1st', '3rd'}, mess
			assert mess['login'] in {self.default('user', 3), self.default('user', 1)}, mess
			
	def test_getMessages_badSid(self):
		self.startTesting()    
		timestamp = int(time.time())
		sid1 =self.send_message()
		sid2 =self.send_message()
		resp = self.send("getMessages",
			{
				"sid": sid1 + sid2,
				"game": "",
				"since": timestamp
			})
		assert resp["result"] == "badSid", resp

	def test_getMessages_badSince_stirng(self):
		timestamp = int(time.time())
		sid =self.send_message()
		resp = self.send("getMessages",
			{
				"sid": sid,
				"game": "",
				"since": "badTimestamp"
			})
		assert resp["result"] == "badSince", resp