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
uploadFolder = "static/uploads/"
app.config["UPLOAD_FOLDER"] = uploadFolder

@app.before_request
def delete_files():
    files_to_delete = session.get('files_to_delete', [])
    if len(files_to_delete) > 20:
        num_files_to_delete = len(files_to_delete) - 20
        files_to_delete = sorted(files_to_delete, key=lambda f: os.path.getctime(os.path.join(uploadFolder, f)))
        files_to_delete = files_to_delete[:num_files_to_delete]
        for file in files_to_delete:
            db = get_db()
            db.execute("""DELETE * FROM games WHERE image = ?;""", (file,))
            db.commit()
            file_path = os.path.join(uploadFolder, file)
            if os.path.exists(file_path):
                os.remove(file_path)

        session['files_to_delete'] = list(set(files_to_delete) - set(files_to_delete))


@app.route("/")
def home():
    db = get_db()
    games = db.execute("""SELECT * FROM games;""").fetchall()
    return render_template("base.html", title="Home Page",games=games)

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
            del session["email"]
            session["email"] = form.email.data
            flash(f"Welcome {form.email.data} You are logged in :)", "success")
            return redirect(request.args.get("next") or url_for("register"))
        
    return render_template("login.html", form=form, title="Login Page")


@app.route('/addgame', methods=['GET','POST'])
def addGame():
    form = AddGameForm()
    if form.validate_on_submit():
        db = get_db()
        gameName = form.gameName.data
        gamePrice = form.gamePrice.data
        gameDiscount = form.gameDiscount.data
        codeStock = form.codeStock.data
        gameDesc = form.gameDesc.data
        uniqueFileName = str(os.urandom(4)) + "_" + form.gameImage.name
        imageFile = request.files[form.gameImage.name]
        clashingGameName = db.execute("""SELECT * FROM games
                                     WHERE name = ?;""", (gameName,)).fetchone()
        if clashingGameName is not None:
            form.gameName.errors.append("Game name already taken, please update.")
        else:
            imageFile.save(os.path.join(app.config["UPLOAD_FOLDER"], uniqueFileName))
            session.setdefault('files_to_delete', []).append(uniqueFileName)
            db.execute("""INSERT INTO games (name, price, discount, stock, descr, image) VALUES (?, ?, ?, ?, ?, ?);""",(gameName, gamePrice, gameDiscount, codeStock, gameDesc, uniqueFileName))
            db.commit()
            flash("Database has been successfully updated.", "success")
    return render_template("addgame.html", title="Add Game Page", form=form)


@app.route('/profile', methods=['GET','POST'])
def profile():
    db = get_db()
    user = db.execute("""SELECT * FROM users WHERE email = ?;""", (session["email"],)).fetchone()
        
    return render_template("profile.html", title="Login Page", user=user )

@app.route('/admin', methods=['GET','POST'])
def admin():
    db = get_db()
    games = db.execute("""SELECT * FROM games;""").fetchall()
        
    return render_template("adminDashboard.html", title="Admin Page", games=games  )

@app.route('/updategame/<int:game_id>', methods=['GET','POST'])
def updategame(game_id):
    db = get_db()
    game = db.execute("""SELECT * FROM games WHERE game_id = ?;""", (game_id,)).fetchone()
        
    return render_template("updateGame.html", title="Update Game Page", game=game  )
