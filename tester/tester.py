# -*- coding: utf-8 -*-

import unittest, MySQLdb, sys

from authentication import AuthTestCase
from map import MapTestCase
from game_preparing import GamePreparingTestCase
from chat import ChatTestCase	
from start import StartTestCase
from ws import WebSocketTestCase
		
if __name__ == '__main__':				# host, port bug
	f = open('log.txt', "w")
	suite = unittest.TestLoader().loadTestsFromTestCase(StartTestCase)
	unittest.TextTestRunner(f).run(suite)
	if len(sys.argv) == 2:
		cases = {
		'A': AuthTestCase,
		'C': ChatTestCase,
		'GP': GamePreparingTestCase,
		'M': MapTestCase,
		'WS': WebSocketTestCase}
		suite = unittest.TestLoader().loadTestsFromTestCase(cases[sys.argv[1]])
		unittest.TextTestRunner(f).run(suite)
	else:
		runner = unittest.TextTestRunner(f)
		unittest.main(testRunner=runner)
	f.close()