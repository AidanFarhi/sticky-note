import os
import requests

from flask import Flask, session, request, render_template, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/", methods=["POST", "GET"])
def index():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return render_template('index.html', message='Please enter a username.')
        if not password:    
            return render_template('index.html', message='Please enter a password.')

        user_check = db.execute("SELECT * FROM users WHERE username = :username", {"username": username})

        if not user_check:
            return render_template('index.html', message="Username not found")

        password_check = db.execute("SELECT * FROM users WHERE password = :password", {"password": password})  

        if not password_check:
            return render_template('index.html', message="Password incorrect.")  

        user_id = db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).fetchone()    
        session["user_id"] = user_id.id

        return render_template('notes.html')

    else:
        return render_template('index.html')    

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template('register.html')

    if request.method == "POST":

        # Get info from form
        username = request.form.get("user-name")
        password = request.form.get("password")

        # No empty fields
        if username is None:
            return render_template('register.html', message='Cannot leave username field blank.')
        if password is None:
            return render_template('register.html', message="Cannot leave password field blank")

        # Check if user already exists
        if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount > 0:
            return render_template('register.html', message="Username already exists")

        # Commit user data to db
        db.execute("INSERT INTO users(username, password) VALUES (:username, :password)", {"username": username, "password": password})    
        db.commit()

        return render_template('index.html', message='Success! User has been created.')

@app.route('/notes', methods=["GET", "POST"])
def notes():

    # Get existing notes for user
    notes = db.execute("SELECT * FROM notes WHERE userid = :userid", {"userid": session["user_id"]}).fetchall()
    
    if request.method == 'POST':

        note = request.form.get('text')
        timestamp = datetime.now()
        userid = session['user_id']

        db.execute('INSERT INTO notes(userid, text, timestamp) VALUES (:userid, :note, :timestamp)', {'userid': userid, 'note': note, 'timestamp': timestamp})
        db.commit()

        notes = db.execute("SELECT * FROM notes WHERE userid = :userid", {"userid": session["user_id"]}).fetchall()

        return render_template('notes.html', notes=notes)

    else:
        return render_template('notes.html', notes=notes)    


