from flask import Flask, render_template, session, redirect, request, url_for, flash, g
from database import get_db, close_db
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm, AddGameForm
from functools import wraps
import os


app = Flask(__name__)
app.teardown_appcontext(close_db)
app.config["SECRET_KEY"] = os.urandom(12)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def home():
    return render_template("index.html", title="Home Page")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = form.password.data
        db = get_db()
        clashingUser = db.execute("""SELECT * FROM users
                                     WHERE username = ?;""", (username,)).fetchone()
        clashingEmail = db.execute("""SELECT * FROM users 
                                     WHERE email = ?;""", (email,)).fetchone()
        if clashingUser is not None:
            form.username.errors.append("Username already taken, please try again.")
        elif clashingEmail is not None:
            form.email.errors.append("Email already taken, please try again.")
        else:
            db.execute("""INSERT INTO users (name, username, email, password) VALUES (?, ?, ?, ?);""",(name, username, email, generate_password_hash(password)))
            db.commit()
            flash(f'Welcome {form.name.data}! Thank you for registering.', "success")
            return redirect(url_for('login'))
    return render_template('register.html', form=form, title="Registration Page")

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db = get_db()
        User = db.execute("""SELECT * FROM users WHERE email = ?;""", (form.email.data,)).fetchone()
        if User is None:
            form.email.errors.append("Email not found, please try again.")
        elif not check_password_hash(User["password"], form.password.data):
            form.password.errors("Wrong password, please try again")
        elif check_password_hash(User["password"], form.password.data) and User["email"] == form.email.data:
            session.clear()
            session["email"] = form.email.data
            flash(f"Welcome {form.email.data} You are logged in :)", "success")
            return redirect(request.args.get("next") or url_for("register"))
        
    return render_template("login.html", form=form, title="Login Page")


@app.route('/addgame', methods=['GET','POST'])
def addGame():
    form = AddGameForm()
    #if form.validate_on_submit():
    return render_template("addgame.html", title="Add Game Page", form=form)
