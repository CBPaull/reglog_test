from flask import Flask, render_template, request, redirect, flash
from flask.ext.bcrypt import Bcrypt
app = Flask(__name__)
bcrypt = Bcrypt(app)
from mysqlconnection import MySQLConnector
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
PASS_REGEX = re.compile(r'\d.*[A-Z]|[A-Z].*\d')
mysql = MySQLConnector(app, 'regcheck')

app.secret_key = "pip"
# our index route will handle rendering our form

@app.route('/')
def index():
    return render_template("registration.html")


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user_query = "SELECT * FROM users WHERE email = :email LIMIT 1"
    query_data = {'id': id, 'email': email}
    user = mysql.query_db(user_query, query_data) # user will be returned in a list
    if bcrypt.check_password_hash(user[0]['pw_hash'], password):
        return render_template("registration.html", email=email, username=user[0]['username'])
    else:
        flash("Password is incorrect")
        return redirect('/')


@app.route('/reg', methods=['POST'])
def users():
    errors = False
    print request.form
    if len(request.form['email']) < 2:
        flash("email cannot be empty!")
        errors = True
    email = request.form['email']
    username = request.form['username']
    email_query = "SELECT email FROM users WHERE email = :email"
    data = {'email': email}
    echeck = mysql.query_db(email_query, data)
    print echeck
    if echeck:
        flash("Email %s already in use" % email)
        errors = True
    if not EMAIL_REGEX.match(request.form['email']):
        flash("must be a valid email!")
        errors = True
    if len(request.form['username']) < 2:
        flash("username cannot be empty!")
        errors = True
    username_query = "SELECT username FROM users WHERE username = '%s'" % username
    ucheck = mysql.query_db(username_query)
    print ucheck
    if ucheck:
        flash("Username %s already in use" % username)
        errors = True
    if len(request.form['password']) < 8:
        flash("password must be 8 characters or longer!")
        errors = True
    if not PASS_REGEX.match(request.form['password']):
        flash("Password must contain an uppercase letter and a number")
        errors = True
    if not (request.form['password'] == request.form['confirm']):
        flash("password and confirmation password must match")
        errors = True

    if errors:
        return redirect('/')
    else:
        password = request.form['password']
        pw_hash = bcrypt.generate_password_hash(password)
        # now we insert the new user into the database
        insert_query = "INSERT INTO users (email, username, pw_hash, created_at, updated_at) VALUES (:email, :username, :pw_hash, NOW(), NOW())"
        query_data = {'email': email, 'username': username, 'pw_hash': pw_hash}
        mysql.query_db(insert_query, query_data)
        return render_template("registration.html", email=email, username=username)


@app.route('/logout', methods=['POST'])
def logout():
    email = None
    username = None
    return redirect('/')
app.run(debug=True)
