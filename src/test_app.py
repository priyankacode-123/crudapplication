"""
This scripts has unit tests for CRUD application
@Author - Priyanka Sirohiya
"""
import os
import unittest
from io import BytesIO
import mysql.connector
from mysql.connector.errors import IntegrityError
from app_flask import app


class TestCrud(unittest.TestCase):
    """
    10 Tests implemented to check whether the application is working properly with both negative and positive scenarios
    """

    def setUp(self):
        self.tester = app.test_client()
        self.record_to_add = {'id': 'baseball', 'symbol': 'base', 'name': 'Bitty'}
        self.record_to_update = {'id': 'baseball', 'symbol': 'base', 'name': 'priyanka'}
        self.record_to_update_with_wrong_id = {'id': 'wrong', 'symbol': 'base', 'name': 'priyanka'}
        self.delete_id = "bitcoin"
        self.to_check_id = "baseball"
        self.filename = "cry.csv"
        self.connection = mysql.connector.connect(host='localhost',
                                                  database='crypto',
                                                  user='root',
                                                  password='1234')

    def test_01_check_homepage_renders_successfully(self):
        """
        Method to check whether the home page renders successfully
        :return: none
        """
        response = self.tester.get("/")
        status_code = response.status_code
        self.assertEqual(status_code, 200)
        self.assertIn(b'Upload the csv file to Mysql Database', response.data)

    def test_02_file_uploaded_successfully(self):
        """
        To check whether the csv is uploaded or not
        :return: none
        """
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
        """
        To check insert view rendering successfully
        :return: none
        """
        response = self.tester.get('/insert')
        self.assertIn(b'<h2>Add Data</h2>', response.data)

    def test_04_record_added_successfully(self):
        """
        To check whether we are able to add a record in DB
        :return: none
        """
        response = self.tester.post('/insert', data=self.record_to_add, follow_redirects=True)
        self.assertIn(b'Data Inserted Successfully', response.data)

    def test_05_record_updated_successfully(self):
        """
        To check record updated successfully or not
        :return: none
        """
        response = self.tester.post('/update',
                                    data=self.record_to_update, follow_redirects=True)
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM cry WHERE id= '{self.record_to_update['id']}'")
        result = cursor.fetchone()
        lst = [list(result)]
        self.assertListEqual(lst[0], list(self.record_to_update.values()))
        self.assertIn(b'Data Updated Successfully', response.data)
        self.assertEqual(response.status_code, 200)

    def test_06_record_deleted_successfully(self):
        """
        To check whether the deleted id is present in database or not
        :return: none
        """
        response = self.tester.get(f'/delete/{self.delete_id}', follow_redirects=True)
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT  * FROM cry where id='{self.delete_id}'")
        result = cursor.fetchone()
        cursor.close()
        self.assertIsNone(result)
        self.assertIn(b'Record Has Been Deleted Successfully', response.data)
        self.assertEqual(response.status_code, 200)

    def test_07_add_duplicate_record_in_db(self):
        """
        To check if system accepts the duplicate value
        :return: none
        """
        # Baseball ID is already present in database
        cursor = self.connection.cursor()
        response = self.tester.post('/insert', data=self.record_to_add, follow_redirects=True)
        with self.assertRaises(IntegrityError):
            cursor.execute("INSERT INTO cry VALUES ('baseball', 'mask', 'priyanka')")
            self.assertIn(b'Data already exists', response.data)

    def test_08_update_data_not_available_in_db(self):
        """
        To update data not available in database
        :return: none
        """
        # trying to update data with "wrong" id
        self.tester.post('/update',
                         data=self.record_to_update_with_wrong_id, follow_redirects=True)
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM cry WHERE id= '{self.record_to_update_with_wrong_id['id']}'")
        result = cursor.fetchone()
        self.assertIsNone(result)

    def test_09_delete_data_not_available_in_db(self):
        """
        To delete data not available in databse
        :return: none
        """
        # trying to delete data with "wrong" id
        self.tester.post(f'/delete/"wrong"', follow_redirects=True)
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM cry WHERE id= 'wrong'")
        result = cursor.fetchone()
        self.assertIsNone(result)

    def test_10_to_check_with_wrong_url(self):
        """
        Rendering wrong url
        :return: none
        """
        response = self.tester.get('pfa')
        self.assertIn(b'Not Found', response.data)


if __name__ == '__main__':
    unittest.main()
