import unittest
import cRequests 


class TestAdd(unittest.TestCase):
    
     def test_add_integer(self):
        """
        Test that the addition of two integers returns the correct total
        """
        w = cRequests.Requests('https://www.libero.it')

        self.assertEqual(1, 1)
