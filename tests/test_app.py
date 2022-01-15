import unittest
from src.App import app
from src.call_csv import csv_to_db



class TestCrud(unittest.TestCase):
    def test_01_check_homepage_renders_successfully(self):
        tester = app.test_client(self)
        response = tester.get("/")
        status_code = response.status_code
        self.assertEqual(status_code, 200)


if __name__ == '__main__':
    unittest.main()
