import os
import requests

from flask import Flask, session, request, render_template, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


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

    if method.get == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return render_template('index.html', message='Please enter a username.')
        if not password:    
            return render_template('index.html', message='Please enter a password.')

        user_check = db.execute("SELECT * FROM users WHERE username = :username", {"username": username})

        if not user_check:
            return render_template('index.html', message="Username not found")

        password_check = db.execute("SELECT * FROM users WHERE password = :password", "password": password)  

        if not password_check:
            return render_template('index.html', message="Password incorrect.")  

        user_id = db.execute("SELECT * FROM users WHERE username = :username AND password = :password" {"username": username, "password": password}).fetchone()    
        session["user_id"] = user_id.id

        return render_template('notes.html')

@app.route("/register", methods=["GET", "POST"])
def register():

    if method == "POST":

