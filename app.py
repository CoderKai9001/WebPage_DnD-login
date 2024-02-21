from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import bcrypt
app = Flask(__name__)

app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Mouli@123'
app.config['MYSQL_DB'] = 'ISIS_DB'

mysql = MySQL(app)
salt = bcrypt.gensalt()
def hash_password(password):
	hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
	return hashed_password.decode('utf-8')

# def index():
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload():
#     if request.method == 'POST':
#         files = request.files.getlist('files[]')

#         for file in files:
#             if file:
#                 filename = file.filename
#                 file.save(filename)

#                 # Insert the filename into MySQL database
#                 cur = mysql.connection.cursor()
#                 cur.execute("INSERT INTO images (filename) VALUES (%s)", (filename,))
#                 mysql.connection.commit()
#                 cur.close()

#         return 'Files uploaded successfully'

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        encrypted_password = hash_password(password)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, encrypted_password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            if account['username'] == 'admin':
                return redirect(url_for('admin_data'))
            else:
                msg = 'Logged in successfully !'
                return render_template('confirmation.html', msg=msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)

@app.route('/home')
def home():
	return render_template('home.html')

@app.route('/preview')
def preview():
	return render_template('preview.html')

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route('/admin_screen')
def admin_data():
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT * FROM accounts')
	accounts = cursor.fetchall()
	return render_template('admin.html', accounts = accounts)

@app.route('/Signup', methods =['GET', 'POST'])
def Signup():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email:
			msg = 'Please fill out the form !'
		else:
			encrypted_password = hash_password(password)
			cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, encrypted_password, email, ))
			cursor.execute('CREATE TABLE `{}` (images BLOB)'.format(username))
			mysql.connection.commit()
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('Signup.html', msg = msg)

if __name__ == '__main__':
    app.run(debug=True)