from index import app 
import unittest
import json

class LobbyTestCase(unittest.TestCase):

    def setUp(self):
        #self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        #app.init_db()

    #def tearDown(self):
        #os.close(self.db_fd)
        #os.unlink(app.config['DATABASE'])    
    
    def send(self, json):
        return self.app.post('/', headers=[('X-Requested-With', 'XMLHttpRequest')], data=json)
    
    def test_empty_db(self):
        resp = self.send("{\
            'action'; 'login',\
        }")
        a = "{'asd': 'ad'}"
        assert json.loads(resp.data) == {'result': 'ok'}

if __name__ == '__main__':
    unittest.main()