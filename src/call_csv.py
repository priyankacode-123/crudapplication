import pandas as pd
import logging
from mysql.connector import connect, errors

logging.basicConfig(filename='logging_crud.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s', filemode='w')

CREATE_TABLE_QUERY = """
                        CREATE TABLE cry(id varchar(200) primary key not null, symbol varchar(250),name varchar(500))
                     """

def csv_to_db(file_name):
    """The function reads a file that was uploaded by the user to the server.
        : param - csv file uploaded by the user."""

    data_frame = pd.read_csv(file_name, index_col=False, delimiter=',')
    try:
        conn = connect(host='localhost',
                       database="crypto",
                       user='root',
                       password='1234')
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            logging.info("You're connected to database: %s", record)
            cursor.execute('DROP TABLE IF EXISTS cry;')
            logging.info('Creating table....')

            cursor.execute(CREATE_TABLE_QUERY)
            logging.info("Table is created....")
            # loop through the data frame
            for i, row in data_frame.iterrows():
                cursor.execute(f"INSERT INTO crypto.cry VALUES {tuple(row)}")
                conn.commit()
    except errors.ProgrammingError as prmg_err:
        logging.error('%s: %s', prmg_err.__class__.__name__, prmg_err)
    except errors.Error as err_e:
        logging.error('%s: %s', err_e.__class__.__name__, err_e)



