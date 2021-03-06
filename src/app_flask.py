"""
The script created an CRUD Application using FLASK framework
Author - Priyanka Sirohiya
"""
import json
import logging
from MySQLdb import IntegrityError, ProgrammingError, Error
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mysqldb import MySQL
from call_csv import csv_to_db, put_json_to_s3

logging.basicConfig(filename='logging_crud.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s', filemode='w')

app = Flask(__name__)
app.secret_key = "flash_priyanka"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_DB'] = 'crypto'
app.config['TESTING'] = True
UPLOAD_FOLDER = 'data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql1 = MySQL(app)


# Root URL
@app.route('/')
def indexs():
    """
    function to redirect to the home page startindex.html
    :return: returns home page whenever server gets started
    """
    # Set The upload HTML template '\templates\startindex.html'
    return render_template('startindex.html')


# Get the uploaded files
@app.route("/", methods=['POST'])
def uploadfiles():
    """
    function to upload csv to db
    :return: renders success.html
    """
    # get the uploaded file
    uploaded_file = request.files['filename']
    if uploaded_file.filename != '':
        csv_to_db(uploaded_file)
        return render_template('success.html')
    logging.info("No file uploaded")
    return render_template('startindex.html')


@app.route("/viewdata")
def index():
    """
    function to redirect to the view page index.html
    :return: renders index page
    """
    try:
        cur = mysql1.connection.cursor()
        cur.execute("SELECT  * FROM cry")
        cry = cur.fetchall()
        cur.close()
        return render_template('index.html', cry=cry)
    except PermissionError as per_err:
        logging.error('%s: %s', per_err.__class__.__name__, per_err)
        return per_err
    except TypeError as type_err:
        logging.error('%s: %s', type_err.__class__.__name__, type_err)
        return type_err


@app.route('/update', methods=['GET', 'POST'])
def update():
    """
    function to perform the update operation referring the key attribute "id"
    :return:  For POST: index page
    """
    if request.method == 'POST':
        try:
            crypto_id = request.form['id']
            symbol = request.form['symbol']
            name = request.form['name']
            cur = mysql1.connection.cursor()
            cur.execute("""
                   UPDATE cry
                   SET symbol=%s, name=%s
                   WHERE id=%s
                """, (symbol, name, crypto_id))
            flash("Data Updated Successfully")
            mysql1.connection.commit()
            with open("cry.json", "r") as json_file:
                data = json.load(json_file)
            for i in data:
                if i["id"] == str(crypto_id):
                    i["symbol"] = symbol
                    i["name"] = name
            with open("cry.json", "w") as json_file:
                json_file.write(json.dumps(data))
            put_json_to_s3("cry.json")
        except PermissionError as per_err:
            logging.error('%s: %s', per_err.__class__.__name__, per_err)
        except TypeError as type_err:
            logging.error('%s: %s', type_err.__class__.__name__, type_err)
    return redirect(url_for('index'))


@app.route('/delete/<string:id_data>', methods=['GET', 'POST'])
def delete(id_data):
    """
    delete the respective row from database with its corresponding id
    :param id_data: primary key value "id" that uniquely identifies the row in DB
    :return: renders index page
    """
    try:
        flash("Record Has Been Deleted Successfully")
        cur = mysql1.connection.cursor()
        cur.execute("DELETE FROM cry WHERE id=%s", (id_data,))
        mysql1.connection.commit()
        with open("cry.json", "r") as json_file:
            data = json.load(json_file)
            data = [i for i in data if not (i["id"] == str(id_data))]
        with open("cry.json", "w") as json_file:
            json.dump(data, json_file)
        put_json_to_s3("cry.json")

        return redirect(url_for('index'))
    except PermissionError as per_err:
        logging.error('%s: %s', per_err.__class__.__name__, per_err)
        return per_err
    except TypeError as type_err:
        logging.error('%s: %s', type_err.__class__.__name__, type_err)
        return type_err


@app.route('/insert')
def add_view():
    """
    creates a INSERT VIEW for entering the data value
    :return: renders insert.html page
    """
    try:
        return render_template('insert.html')
    except PermissionError as per_err:
        logging.error('%s: %s', per_err.__class__.__name__, per_err)
        return per_err
    except TypeError as type_err:
        logging.error('%s: %s', type_err.__class__.__name__, type_err)
        return type_err


@app.route('/insert', methods=['POST', 'GET'])
def insert():
    """
    insert the value in database
    :return: POST: renders index page
    """

    if request.method == "POST":
        try:
            crypto_id = request.form['id']
            symbol = request.form['symbol']
            name = request.form['name']
            cur = mysql1.connection.cursor()

            cur.execute("INSERT INTO cry (id,symbol, name) "
                        "VALUES (%s, %s, %s)", (crypto_id, symbol, name))
            flash("Data Inserted Successfully")
            mysql1.connection.commit()
            entry = {'id': crypto_id, 'symbol': symbol, 'name': name}
            with open("cry.json", "r") as json_file:
                data = json.load(json_file)
            data.append(entry)
            with open("cry.json", "w") as json_file:
                json.dump(data, json_file)
            put_json_to_s3("cry.json")

        except IntegrityError as in_err:
            logging.info("Integrity Error raised")
            logging.error('%s: %s', in_err.__class__.__name__, in_err)
            flash("Data already exists")
            return redirect(url_for('index'))
        except ProgrammingError as db_err:
            logging.info("Programming Error raised")
            logging.error('%s: %s', db_err.__class__.__name__, db_err)
        except Error as err:
            logging.error('%s: %s', err.__class__.__name__, err)
        else:
            return redirect(url_for('index'))
    return render_template("insert.html")


if __name__ == "__main__":
    app.run(host="localhost", debug=True)
