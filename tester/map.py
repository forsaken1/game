# -*- coding: utf-8 -*-
from base import *

class MapTestCase(BaseTestCase):
	def test_uploadMap_ok(self):
		self.upload_map()
		
	def test_uploadMap_badMap(self):
		resp = self.upload_map(map = ['.**..'], is_ret = True)
		assert resp["result"] == "badMap", resp

	def test_uploadMap_badMap_unexpected_letter(self):
		resp = self.upload_map(map = ['.q..'], is_ret = True)
		assert resp["result"] == "badMap", resp
	
	def test_uploadMap_badMap_singleStr(self):
		resp = self.upload_map(map = '...', is_ret = True)
		assert resp["result"] == "badMap", resp
	
	def test_uploadMap_badMap_unpair_tps(self):
		resp = self.upload_map(map =  ['2.', '.1'], is_ret = True)
		assert resp["result"] == "badMap", resp

	def test_uploadMap_badSid(self):
		self.startTesting()
		resp = self.upload_map(is_ret = True, sid = "badSid")
		assert resp["result"] == "badSid", resp

		
	def test_uploadMap_badMaxPlayers(self):
		resp = self.upload_map(is_ret = True, maxPlayers = -10)
		assert resp["result"] == "badMaxPlayers", resp

	def test_uploadMap_mapExists(self):
		self.upload_map(name = "MapMap")		
		resp = self.upload_map(is_ret = True, name = "MapMap")
		assert resp["result"] == "mapExists", resp		
		
	def test_getMaps_ok(self):	
		self.startTesting()	
		self.upload_map()
		resp = self.get_map(is_ret = True)
		assert resp.has_key('maps'), resp
		maps = [
			{
				"name": self.default('map', 3),
				"map": def_map_scheme,
				"maxPlayers": 8,
			},		
			{
				"name": self.default('map', 2),
				"map": def_map_scheme,
				"maxPlayers": 8,
			},
			{
				"name": self.default('map', 1),
				"map": def_map_scheme,
				"maxPlayers": 8,
			}
		]
		assert len(resp["maps"]) == 3, resp
		for map in resp["maps"]:
			assert map.has_key('id') and type(map['id']) is int, map
			del map['id']
		for map in maps:		
			assert resp["maps"].count(map) == 1, [map, resp]
		del resp["maps"]
		assert resp["result"] == "ok", resp	

	def test_getMaps_badSid(self):
		self.startTesting()
		sid = self.upload_map()
		resp = self.send("getMaps",{"sid": sid+"1"})
		assert resp["result"] == "badSid", resp			
		