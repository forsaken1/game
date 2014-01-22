# -*- coding: utf-8 -*-

import unittest, MySQLdb, sys
import sys
import os.path
sys.path.append(
os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from authentication import AuthTestCase
from map import MapTestCase
from game_preparing import GamePreparingTestCase
from chat import ChatTestCase	
from start import StartTestCase
from ws import WebSocketTestCase
from fire import FireTestCase
	
def tester(case = 'ALL'):
	f = open('log.txt', "w")
	suite = unittest.TestSuite()
	suite.addTest(StartTestCase("test_startTesting"))
	runner = unittest.TextTestRunner(f)
	runner.run(suite)
	suite = unittest.TestSuite()
	suite.addTest(StartTestCase("test_getGameConsts_ok"))
	runner.run(suite)
	if case == 'ALL':
		unittest.main(testRunner=runner)
	else:
		cases = {
		'A': AuthTestCase,
		'C': ChatTestCase,
		'GP': GamePreparingTestCase,
		'M': MapTestCase,
		'WS': WebSocketTestCase,
		'F': FireTestCase}
		if cases.has_key(case):
			suite = unittest.TestLoader().loadTestsFromTestCase(cases[case])
			runner.run(suite)
		else:
			has_test = False
			for c in cases.values():
				if hasattr(c, case):
					has_test = True 
					suite = unittest.TestSuite()
					suite.addTest(c(case))
					runner.run(suite)
					break
			if not has_test: print "not such test/test case"
	f.close()		
	
	
if __name__ == '__main__':
	if len(sys.argv) == 2:
		tester(sys.argv[1])
	else:
		tester()
	
	