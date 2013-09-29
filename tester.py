from run import app 
import json, unittest, re, MySQLdb

def send(test, query):
    query = json.dumps(query)
    resp = test.app.post('/', data=query)
    resp = json.loads(resp.data)
    if resp.has_key('message'):
        del resp['message']
    return resp

def signup_user(test, login, passwd = "pass"):
    resp = send(test, 
    {
        "action": "signup",
        "params": 
        {
            "login": login,
            "password": passwd 
        }
    })
    assert resp == {"result": "ok"}, resp    

def signin_user(test, login, passwd = "pass"):
    resp = send(test, 
    {
        "action": "signin",
        "params": 
        {
            "login": login,
            "password": passwd 
        }
    })
    sid = resp['sid']
    assert re.match('^\w+$', sid), sid
    assert resp == {"result": "ok", "sid": sid}, resp
    return sid
    
def create_db():
    con = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='',)
    cursor = con.cursor()
    cursor.execute('CREATE DATABASE IF NOT EXISTS test')
    con.close()
    con = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='test')
    cursor = con.cursor()    
    sql = '''CREATE TABLE IF NOT EXISTS `users` (
			`id` int(11) NOT NULL AUTO_INCREMENT,
			`online` bit(1) NOT NULL DEFAULT b'0',
			`sid` varchar(64) CHARACTER SET latin1,
			`login` varchar(255) CHARACTER SET latin1 NOT NULL,
			`password` varchar(255) CHARACTER SET latin1 NOT NULL,
			`game_id` int(11),
			`last_connection` date,
			PRIMARY KEY (`id`),
			KEY `id` (`id`)
			) DEFAULT CHARSET=utf8 AUTO_INCREMENT=2 ;
			
			CREATE TABLE IF NOT EXISTS `messages` (
			`id` int(11) NOT NULL AUTO_INCREMENT,
			`login_id` int(11) NOT NULL,
			`text` varchar(1024) CHARACTER SET latin1 NOT NULL,
			`time` date NOT NULL,
			`game_id` int(11) NOT NULL,
			PRIMARY KEY (`id`)
			) DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;			
           '''
    cursor.execute(sql)    
    con.close()
    
def drop_db():
    con = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='',)    
    cursor = con.cursor()
    cursor.execute('DROP DATABASE IF EXISTS test')
    con.close()	
           
def setup(test):
    app.config["TESTING"] = True
    test.app = app.test_client()    
    create_db()

#def tearDown(test):
    #os.close(test.db_fd)
    #os.unlink(app.config["DATABASE"])

    
class AuthTestCase(unittest.TestCase):
    
    setUp = setup    
    def tearDown(test):
        drop_db()
    
    def test_unknown_action1(self):
        resp = send(self, 
        {
            "params": {
                "login": "user",
                "password": "pass" 
            } 
        })
        assert resp == { "result": "unknownAction" }, resp   
        
    def test_unknown_action2(self):
        resp = json.loads(self.app.post('/', data="fooooooo").data)
        if resp.has_key('message'):
            del resp['message']        
        assert resp == { "result": "unknownAction" }, resp
        
    def test_signup_ok(self):
        signup_user(self, 'user1')
        
    def test_signup_bad_pass(self):
        resp = send(self, 
        {
            "action": "signup",
            "params": 
            {
                "login": "user2",
                "password": "p" 
            }
        })
        assert resp == { "result": "badPassword" }, resp

    def test_signup_bad_login1(self):
        resp = send(self, 
        { 
            "action": "signup",
            "params": 
            {
                "login": "u",
                "password": "pass3" 
            } 
        })
        assert resp == { "result": "badLogin" }, resp
 
    def test_signup_bad_login2(self):
        resp = send(self, 
        { 
            "action": "signup",
            "params": 
            {
                "login": "ThisStringConsistMoreThen40LattersMoreMore",
                "password": "pass3" 
            }
        })
        assert resp == { "result": "badLogin" }, resp
        
    def test_signup_already_exists(self):
        signup_user(self,'user4', 'pass4')
        resp = send(self, 
        { 
            "action": "signup", 
            "params": 
            {
                "login": "user4",
                "password": "pass4" 
            } 
        })
        assert resp == { "result": "userExists" }, resp
 
    def test_signin_ok(self):
        signup_user(self,'user5')
        signin_user(self,'user5')        
 
    def test_signin_bad_combi(self):
        signup_user(self,'user6')    
        resp = send(self, 
        { 
            "action": "signin",
            "params": 
            {
                "login": "user6",
                "password": "pass6" 
            } 
        })
        assert resp == { "result": "incorrect" }, resp
        
    def test_signout_ok(self):       
        signup_user(self,'user7')
        sid = signin_user(self,'user7')    
        resp = send(self, 
        { 
            "action": "signout",
            "params": 
            {    
                "sid": sid
            } 
        })        
        assert resp == {"result": "ok"}, resp       

	def test_signout_bad_sid(self):
		drop_db()
		create_db()
		signup_user(self,'user8')
		sid1 = signin_user(self,'user8')   
		signup_user(self,'user8')
		sid2 = signin_user(self,'user8')   		
		resp = send(self, 
		{ 
			"action": "signout",
			"params": 
			{    
				"sid": sid1 + sid2
			} 
		})        
		assert resp == {"result": "badSid"}, resp           
    
class ChatTestCase(unittest.TestCase):
    
    setUp = setup    
    def tearDown(test):
        drop_db()   
	
	def test_sendMessage_bad_sid(self):
		drop_db()
		create_db()
		signup_user(self,'user8')
		sid1 = signin_user(self,'user8')   
		signup_user(self,'user8')
		sid2 = signin_user(self,'user8')   		
		resp = send(self, 
		{ 
			"action": "signout",
			"params": 
			{    
				"sid": sid1 + sid2
			} 
		})        
		assert resp == {"result": "badSid"}, resp        	
    
if __name__ == '__main__':
   log_file = 'log.txt'
   f = open(log_file, "w")
   runner = unittest.TextTestRunner(f)
   unittest.main(testRunner=runner)
   f.close()