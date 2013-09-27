from run import app 
import unittest
import json
import re

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
    assert re.match('\w+$', sid), sid
    assert resp == {"result": "ok", "sid": sid}, resp
    return sid
    
def setup(test):
    app.config["TESTING"] = True
    test.app = app.test_client()    

#def tearDown(test):
    #os.close(test.db_fd)
    #os.unlink(app.config["DATABASE"])

    
class AuthTestCase(unittest.TestCase):
    
    setUp = setup    

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

   # def test_signout_bad_sid(self):

if __name__ == '__main__':
   log_file = 'log.txt'
   f = open(log_file, "w")
   runner = unittest.TextTestRunner(f)
   unittest.main(testRunner=runner)
   f.close()