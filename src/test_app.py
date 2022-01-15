import os
import unittest
from io import BytesIO

from MySQLdb import IntegrityError
from mysql.connector.errors import IntegrityError, DatabaseError

from App import app


class TestCrud(unittest.TestCase):

    def setUp(self):
        self.tester = app.test_client()
        self.record_to_add = {'id': 'baseball', 'symbol': 'base', 'name': 'Bitty'}
        self.record_to_update = {'id': 'baseball', 'symbol': 'base', 'name': 'priyankaSirohiya'}
        self.delete_id = "bitcoin"
        self.to_check_id = "bitcoin"
        self.filename = "cry.csv"

    def test_01_check_homepage_renders_successfully(self):
        response = self.tester.get("/")
        status_code = response.status_code
        self.assertEqual(status_code, 200)
        self.assertIn(b'Upload the csv file to Mysql Database', response.data)

    def test_02_file_uploaded_successfully(self):
        with open(os.path.join(os.path.dirname(__file__), 'data/cry.csv'),
                  'rb') as file:
            data = {
                'field': 'value',
                'filename': (BytesIO(file.read()), self.filename)
            }
            response = self.tester.post('/', buffered=True, data=data,
                                        content_type='multipart/form-data',
                                        follow_redirects=True)
            self.assertIn(b'<h3>Data uploaded successfully</h3>', response.data)

    def test_03_insert_view_rendered_successfully(self):
        response = self.tester.get('/insert')
        self.assertIn(b'<h2>Add Data</h2>', response.data)

    def test_04_record_added_successfully(self):
        response = self.tester.post('/insert', data=self.record_to_add, follow_redirects=True)
        self.assertIn(b'Data Inserted Successfully', response.data)

    def test_05_record_updated_successfully(self):
        response = self.tester.post('/update',
                                    data=self.record_to_update, follow_redirects=True)
        self.assertIn(b'Data Updated Successfully', response.data)
        self.assertEqual(response.status_code, 200)

    def test_06_record_deleted_successfully(self):
        response = self.tester.get(f'/delete/{self.delete_id}', follow_redirects=True)
        self.assertIn(b'Record Has Been Deleted Successfully', response.data)
        self.assertEqual(response.status_code, 200)

    def test_07_add_duplicate_record_in_db(self):
        # Baseball ID is already present in database
        #with self.assertRaises(IntegrityError):
        response = self.tester.post('/insert', data=self.record_to_add, follow_redirects=True)
        self.assertEqual(response.status_code, 1062)

    def test_08_update_data_not_available_in_db(self):
        wrong_id = 'wrong'  # id not available
        response = self.tester.post(f'/update', data=wrong_id, follow_redirects=True)
        self.assertNotIn(f"{wrong_id}".encode(), response.data)

    def test_09_delete_data_not_available_in_db(self):
        wrong_id = 'wrong'  # id not available
        response = self.tester.get(f'/delete/{wrong_id}', follow_redirects=True)
        self.assertNotIn(f"{wrong_id}".encode(), response.data)

    def test_10_to_check_with_wrong_url(self):
        response = self.tester.get('pfa')
        self.assertIn(b'Not Found', response.data)




if __name__ == '__main__':
    unittest.main()
