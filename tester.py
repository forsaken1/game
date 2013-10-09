# -*- coding: utf-8 -*-

from run import app
import json, unittest, re, MySQLdb, time, process, requests
from websocket import create_connection

host, port = 'localhost', '5000'

def send(test, action, params):
    query = json.dumps(
    {
        "action": action,
        "params": params
    })
    #resp = test.app.post('/', data=query)
    resp = requests.post("http:/" + host + ":" + port, data=query)
    #resp = json.loads(resp.data)
    resp = json.loads(resp.text)
    if resp.has_key('message'):
        del resp['message']
    return resp

def drop_db():
    con = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='',)
    cursor = con.cursor()
    cursor.execute('DROP DATABASE IF EXISTS test')
    con.close()

counter = {'users': 0, 'games': 0}

def count(item):  
    if not counter.has_key(item): raise AssertionError('not such table:' + item)
    else:
        counter[item] += 1
        return str(counter[item] - 1)

def truncate_db():
    query = json.dumps({"action": "startTesting"})
    resp = requests.post("http://" + host + ":" + port, data=query)
    assert resp == {"result": "ok"}, resp

def setup(test):
    test.u = 0
    app.config["TESTING"] = True
    test.app = app.test_client()
    process.create_db('test')
    truncate_db()        

def signup_user(test, login = "user" + count('users'), passwd = "pass"):
    resp = send(test, "signup", {"login": login,"password": passwd })
    assert resp == {"result": "ok"}, resp

def signin_user(test, login = "user" + count('users'), passwd = "pass"):
    signup_user(test, login, passwd)
    resp = send(test,"signin", {"login": login,"password": passwd})
    sid = resp['sid']
    assert re.match('^\w+$', sid), sid
    assert resp == {"result": "ok", "sid": sid}, resp
    return sid

class AuthTestCase(unittest.TestCase):

    setUp = setup
    def tearDown(test):
        drop_db()
    
    def test_startTesting(self):
        truncate_db()
    
    def test_unknown_action_not_action(self):
        query = json.dumps(
        {
            "params":
            {
                "login": "user",
                "password": "pass"
            }
        })
        resp = self.app.post('/', data=query)
        resp = json.loads(resp.data)
        if resp.has_key('message'):
            del resp['message']
        assert resp == { "result": "unknownAction" }, resp

    def test_unknown_action_isnot_json(self):
        resp = json.loads(self.app.post('/', data="fooooooo").data)
        if resp.has_key('message'):
            del resp['message']
        assert resp == { "result": "unknownAction" }, resp

    def test_unknown_action(self):
        resp = send(self, "unknown_action", {"login": "userr","password": "pass" })
        if resp.has_key('message'):
            del resp['message']
        assert resp == { "result": "unknownAction" }, resp

    def test_signup_ok(self):
        signup_user(self)

    def test_signup_bad_pass(self):
        resp = send(self, "signup",{"login": "user" + count('users'),"password": "p"})
        assert resp == { "result": "badPassword" }, resp

    def test_signup_bad_login1(self):
        resp = send(self, "signup",{"login": "u","password": "pass3"})
        assert resp == { "result": "badLogin" }, resp

    def test_signup_bad_login2(self):
        resp = send(self, "signup",{"login": "ThisStringConsistMoreThen40LattersNeedSomeMore", "password": "pass3"})
        assert resp == { "result": "badLogin" }, resp

    def test_signup_already_exists(self):
        signup_user(self)
        resp = send(self,"signup", {"login": "user" + str(counter['users']), "password": "pass"})
        assert resp == { "result": "userExists" }, resp

    def test_signin_ok(self):
        signin_user(self)

    def test_signin_bad_combi(self):
        signup_user(self)
        resp = send(self,"signin",{"login": "user" + str(counter['users'] - 1), "password": "bad_pass"})
        assert resp == { "result": "incorrect" }, resp

    def test_signout_ok(self):
        sid = signin_user(self)
        resp = send(self, "signout", {"sid": sid})
        assert resp == {"result": "ok"}, resp

    def test_signout_bad_sid(self):
        truncate_db()
        sid1 = signin_user(self)
        sid2 = signin_user(self)
        resp = send(self, "signout", {"sid": sid1 + sid2})
        assert resp == {"result": "badSid"}, resp

def send_message(test, login = "user" + count('users'), game = "", text = "some_text"):
    sid = signin_user(test, login)
    resp = send(test,"sendMessage",{"sid": sid,"game": game,"text": text})
    assert resp == {"result": "ok"}, resp
    return sid

class ChatTestCase(unittest.TestCase):

    setUp = setup
    def tearDown(test):
        drop_db()

    def test_sendMessage_ok(self):
        send_message(self)

    def test_sendMessage_ok_empty(self):
        send_message(self, text = "")

    def test_sendMessage_ok_cyr(self):
        send_message(self, text = "привет!")

#   def test_sendMessage_ok_from_game(self):
    def test_sendMessage_badSid(self):
        truncate_db()
        sid1 = signin_user(self)
        sid2 = signin_user(self)
        resp = send(self, "sendMessage", {"sid": sid1 + sid2,"game": "","text": "hello"})
        assert resp == {"result": "badSid"}, resp

#    def test_sendMessage_badGame(self):

    def test_getMessages_ok(self):
        truncate_db()
        send_message(self)
        time.sleep(5)
        timestamp1 = int(time.time())
        sid1 = send_message(self)
        time.sleep(5)
        timestamp2 = int(time.time())
        sid2 = send_message(self)
        resp = send(self, "getMessages",
            {
                "sid": sid1,
                "game": "",
                "since": timestamp1
            })
        mass = resp['messages']
        del resp['messages'][0]['time']
        del resp['messages'][1]['time']
        assert mass[0]['time'] < mass[1]['time']
        assert resp == {"result": "ok", "message": [
            {
                "text": "some_text",
                "login": "user" + str(counter['users'] - 2)
            },
            {
                "text": "some_text",
                "login": "user" + str(counter['users'] - 1)
            }]}, resp

    def test_getMessages_badSid(self):
        truncate_db()    
        timestamp = int(time.time())
        sid1 = send_message(self)
        sid2 = send_message(self)
        resp = send(self, "getMessages",
            {
                "sid": sid1 + sid2,
                "game": "",
                "since": timestamp
            })
        assert resp == {"result": "badSid"}, resp

    def test_getMessages_badSince_stirng(self):
        timestamp = int(time.time())
        sid = send_message(self)
        resp = send(self, "getMessages",
            {
                "sid": sid,
                "game": "",
                "since": "badTimestamp"
            })
        assert resp == {"result": "badSince"}, resp

def create_game(test, is_ret = False, login = "user" + count('users'), name = "game" + count('games'), map = "map", maxPlayers = 8):
    sid = signin_user(test,login)
    resp = send(test, "createGame",
        {
            "sid": sid,
            "name": name,
            "map": map,
            "maxPlayers": maxPlayers
        })
    if is_ret: return resp
    assert resp == {"result": "ok"}, resp
    return sid

def join_game(test, game, login = "user" + count('users')):
    sid = signin_user(test, login)
    resp = send(test, "joinGame",
        {
            "sid": sid,
            "game": game,
        })
    assert resp == {"result": "ok"}, resp
    return sid

def get_game(test, is_ret = False, login = "user" + count('users'), name = "game" + count('games'), map = "map", maxPlayers = 8):
    if not is_ret: truncate_db()
    create_game(test)
    sid = signin_user(test)
    resp = send(test, "getGames", {"sid": sid})
    if is_ret: return resp
    assert resp.has_key('games'), resp
    game = resp['games'][0]
    assert game.has_key('id') or type(game['id']) is int, game
    id = game["id"]
    del game["id"]
    assert resp == {"result": "ok", "games": [
    {
        "name": "game" + str(counter['games']-1),
        "map": "map",
        "maxPlayers": 8,
        "players": [],
        "status": "running"
    }]}, resp
    return id
{u'games': [{u'status': u'running', u'map': u'map', u'name': u'game0', u'maxPlayers': 8, u'players': [{u'login': u'user3'}], u'sid': u'537f37481182c9334d206bb2ecf6259ad7a865523a50d7373cd55508acef5fe5'}], u'result': u'ok'}

class GamePreparingTestCase(unittest.TestCase):

    setUp = setup
    def tearDown(test):
        drop_db()
        
    def test_createGame_ok(self):
        create_game(self)

    def test_createGame_badSid(self):
        truncate_db()
        sid1 = signin_user(self)
        sid2 = signin_user(self)
        resp = send(self, "createGame",
            {
                "sid": sid1 + sid2,
                "name": "RakiSyuda",
                "map": "bestMap",
                "maxPlayers": 8
            })
        assert resp == {"result": "badSid"}, resp

    def test_createGame_badSid_signInOut(self):
        truncate_db()
        sid = signin_user(self,'user35')
        resp = send(self, "signout",{"sid": sid})
        assert resp == {"result": "ok"}, resp
        resp = send(self, "createGame",
            {
                "sid": sid,
                "name": "RakiSyuda1",
                "map": "bestMap",
                "maxPlayers": 8
            })
        assert resp == {"result": "badSid"}, resp

    def test_createGame_badName(self):
        sid = signin_user(self)
        resp = create_game(self, is_ret = True, name = "")
        assert resp == {"result": "badName"}, resp

    def test_createGame_badMap(self):
        sid = signin_user(self)
        resp = send(self, "createGame",
            {
                "sid": sid,
                "name": "game3",
                "map": "notInBase",                # there isn't such map in DB
                "maxPlayers": 8
            })
        assert resp == {"result": "ok"}, resp      #   "result": "badMap"

    def test_createGame_badMaxPlayers(self):
        sid = signin_user(self)
        resp = create_game(self, is_ret = True, maxPlayers = "badMaxPl")
        assert resp == {"result": "badMaxPlayers"}, resp

    def test_createGame_gameExists(self):
        create_game(self)
        sid = signin_user(self)
        resp = create_game(self, is_ret = True, name = "game" + str(counter['games']-1))
        assert resp == {"result": "gameExists"}, resp

    def test_getGames_ok(self):
        truncate_db()
        create_game(self)

        resp = get_game(self, is_ret = True)
        assert resp.has_key('games'), resp
        games = [
            {
                "name": "game" + str(counter['games'] - 2),
                "map": "map",
                "maxPlayers": 8,
                "players": [],
                "status": "running"
            },
            {
                "name": "game" + str(counter['games'] - 1),
                "map": "map",
                "maxPlayers": 8,
                "players": [],
                "status": "running"
            }
        ]
        for game in resp["games"]:
            assert game.has_key('id') and type(game['id']) is int, game
            for i in range(2):
                if games[i] == game:
                    games[i] = 0
                    return

        assert game == [0,0], resp
        del resp["games"]
        assert resp == {"result":"ok"}, resp

    def test_getGames_badSid(self):
        truncate_db()
        sid = create_game(self)
        resp = send(self, "getGames",{"sid": sid+"1"})
        assert resp == {"result": "badSid"}, resp

    def test_joinGame_ok(self):
        game = get_game(self)
        join_game(self, game = game)

    def test_joinGame_gameFull(self, maxPlayers = 3):
        game = get_game(self)
        for i in range(2):
            join_game(self, game = game)
        sid = signin_user(test, login)
        resp = send(test, "joinGame",
            {
                "sid": sid,
                "game": game,
            })
        assert resp == {"result": "gameFull"}, resp

    def test_joinGame_badGame(self):
        game = get_game(self)
        resp = send(self, "joinGame",
            {
                "sid": sid,
                "game": game+1
            })
        assert resp == {"result": "badGame"}, resp
        # already in game test

    def test_leaveGame_ok(self):
        game = get_game(self)
        sid = join_game(self, game = game)
        resp = send(self, "leaveGame", {"sid": sid})
        assert resp == {"result": "ok"}, resp

    def test_leaveGame_alreadyLeave(self):
        game = get_game(self)
        sid = join_game(self, game = game)
        resp = send(self, "leaveGame", {"sid": sid})
        assert resp == {"result": "ok"}, resp
        resp = send(self, "leaveGame", {"sid": sid})
        assert resp == {"result": "notInGame"}, resp

    def test_leaveGame_alreadyLeave(self):
        game = get_game(self)
        join_game(self, game = game)
        sid = signin_user(self)
        resp = send(self, "leaveGame", {"sid": sid})
        assert resp == {"result": "notInGame"}, resp

class test_ws(unittest.TestCase):
	def setUp(self):
		self.ws = create_connection('ws://' + host + ':' + port)

	def test_ws(self):
		self.ws.send('100')
		resp = self.ws.recv()
		assert  resp == '100', resp
		
if __name__ == '__main__':
   log_file = 'log.txt'
   f = open(log_file, "w")
   runner = unittest.TextTestRunner(f)
   unittest.main(testRunner=runner)
   f.close()