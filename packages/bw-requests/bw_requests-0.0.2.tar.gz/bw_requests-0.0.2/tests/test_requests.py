import unittest
from bw_requests.bw_requests import Requests
import warnings

class TestBwRequest(unittest.TestCase):
        
    def setUp(self):
        warnings.simplefilter('ignore',category=ResourceWarning)

    def test_request_get_simple(self):
        service=Requests('https://www.libero.it').get('',headers={"Content-Type": 'application/json; charset=UTF-8'})
        self.assertEqual(service.status_code, 200)
        
    def test_request_get_with_useragent(self):
        service=Requests('https://www.libero.it').get('',headers={"Content-Type": 'application/json; charset=UTF-8', 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0'})
        self.assertEqual(service.status_code, 200)
        
if __name__ == '__main__':
    unittest.main()