# -*- coding: utf-8 -*-

import unittest, MySQLdb, sys

from authentication import AuthTestCase
from map import MapTestCase
from game_preparing import GamePreparingTestCase
from chat import ChatTestCase	
from start import StartTestCase
from ws import WebSocketTestCase
	
def tester(case = 'ALL'):
	f = open('log.txt', "w")
	suite = unittest.TestSuite()
	suite.addTest(StartTestCase("test_startTesting"))
	runner = unittest.TextTestRunner(f)
	runner.run(suite)
	suite = unittest.TestSuite()
	suite.addTest(StartTestCase("test_getGameConsts_ok"))
	runner.run(suite)
	cases = {
	'A': AuthTestCase,
	'C': ChatTestCase,
	'GP': GamePreparingTestCase,
	'M': MapTestCase,
	'WS': WebSocketTestCase}
	if cases.has_key(case):
		suite = unittest.TestLoader().loadTestsFromTestCase(cases[case])
		runner.run(suite)
	else:
		unittest.main(testRunner=runner)
	f.close()		
	
	
if __name__ == '__main__':				# host, port bug
	if len(sys.argv) == 2:
		tester(sys.argv[1])
	else:
		tester()
	
	