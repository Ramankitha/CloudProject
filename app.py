import sqlite3

from flask import Flask, request, g, render_template, send_file

DATABASE = '/Users/ramankithap/PycharmProjects/CloudProject/example.db'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_to_database():
    return sqlite3.connect(DATABASE)

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = connect_to_database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def execute_query(query, args=()):
    cur = get_db().execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows

def commit():
    get_db().commit()

@app.route("/")
def hello():
    return render_template('mainpage.html')

@app.route('/login', methods =['POST', 'GET'])
def login():
    message = ''
    if request.method == 'POST' and str(request.form['username']) !="" and str(request.form['password']) != "":
        username = str(request.form['username'])
        password = str(request.form['password'])
        result = execute_query("""SELECT firstname,lastname,email,count  FROM users WHERE Username  = (?) AND Password = (?)""", (username, password ))
        if result:
            for row in result:
                return responsePage(row[0], row[1], row[2], row[3])
        else:
            message = 'Invalid Username or Password!'
    elif request.method == 'POST':
        message = 'Enter your Username and password!'
    return render_template('mainpage.html', message = message)

@app.route('/registrationpage', methods =['GET', 'POST'])
def registrationpage():
    message = ''
    if request.method == 'POST' and str(request.form['username']) !="" and str(request.form['password']) !="" and str(request.form['firstname']) !="" and str(request.form['lastname']) !="" and str(request.form['email']) !="":
        username = str(request.form['username'])
        password = str(request.form['password'])
        firstname = str(request.form['firstname'])
        lastname = str(request.form['lastname'])
        email = str(request.form['email'])
        uploaded_file = request.files['textfile']
        if not uploaded_file:
            filename = None
            word_count = None
        else :
            filename = uploaded_file.filename
            word_count = getNumberOfWords(uploaded_file)
        result = execute_query("""SELECT *  FROM users WHERE Username  = (?)""", (username, ))
        if result:
            message = 'Account exists!'
        else:
            result1 = execute_query("""INSERT INTO users (username, password, firstname, lastname, email, count) values (?, ?, ?, ?, ?, ? )""", (username, password, firstname, lastname, email, word_count, ))
            commit()
            result2 = execute_query("""SELECT firstname,lastname,email,count  FROM users WHERE Username  = (?) AND Password = (?)""", (username, password ))
            if result2:
                for row in result2:
                    return responsePage(row[0], row[1], row[2], row[3])
    elif request.method == 'POST':
        message = 'Missing Fields!'
    return render_template('registrationpage.html', message = message)

@app.route("/download")
def download():
    path = "Limerick.txt"
    return send_file(path, as_attachment=True)

def getNumberOfWords(file):
    data = file.read()
    words = data.split()
    return str(len(words))

def responsePage(firstname, lastname, email, count):
    return """ First Name :  """ + str(firstname) + """ <br> Last Name : """ + str(lastname) + """ <br> Email : """ + str(email) + """ <br> Word Count : """ + str(count) + """ <br><br> <a href="/download" >Download</a> """

if __name__ == '__main__':
  app.run()
