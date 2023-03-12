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
def loggedInUser():
    g.user = session.get("email", None)

def login_required(view): 
    @wraps(view) 
    def wrapped_view(*args, **kwargs): 
        if g.user is None: 
            return redirect(url_for("login", next=request.url)) 
        return view(*args, **kwargs) 
    return wrapped_view

def admin_required(view): 
    @wraps(view) 
    def wrapped_view(*args, **kwargs): 
        if g.user != "admin1": 
            return redirect(url_for("login", next=request.url)) 
        return view(*args, **kwargs) 
    return wrapped_view

@app.before_request
def delete_files():
    gamesImages = db.execute("""SELECT image FROM games;""").fetchall()
    if len(gamesImages) > 10:
        num_files_to_delete = len(gamesImages) - 10
        gamesImages = sorted(gamesImages, key=lambda f: os.path.getctime(os.path.join(uploadFolder, f)))
        gamesImages = gamesImages[:num_files_to_delete]
        for file in gamesImages:
            db = get_db()
            db.execute("""DELETE * FROM games WHERE image = ?;""", (file,))
            db.commit()
            file_path = os.path.join(uploadFolder, file)
            if os.path.exists(file_path):
                os.remove(file_path)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/home")
def index():
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
            session.clear()
            session["email"] = form.email.data
            flash(f"Welcome {form.email.data} You are logged in :)", "success")
            return redirect(request.args.get("next") or url_for("register"))
        
    return render_template("login.html", form=form, title="Login Page")


@app.route('/addgame', methods=['GET','POST'])
@admin_required
def addgame():
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
            return redirect(url_for("admin"))
    return render_template("addgame.html", title="Add Game Page", form=form)


@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    db = get_db()
    user = db.execute("""SELECT * FROM users WHERE email = ?;""", (session["email"],)).fetchone()
    return render_template("profile.html", title="Login Page", user=user)

@app.route('/admin', methods=['GET','POST'])
@admin_required
def admin():
    db = get_db()
    games = db.execute("""SELECT * FROM games;""").fetchall()
        
    return render_template("adminDashboard.html", title="Admin Page", games=games  )

@app.route('/updategame/<int:game_id>', methods=['GET','POST'])
@admin_required
def updategame(game_id):
    db = get_db()
    game = db.execute("""SELECT * FROM games WHERE game_id = ?;""", (game_id,)).fetchone()
    if request.method == "POST":
        gameName = request.form.get("gameName")
        gamePrice = request.form.get("gamePrice")
        gameDiscount = request.form.get("gameDiscount")
        gameStock = request.form.get("gameStock")
        gameDesc = request.form.get("gameDesc")
        db.execute("""UPDATE games SET name = ?, price = ?, discount = ?, stock = ?, descr = ? WHERE game_id = ?;""",
            (gameName, gamePrice, gameDiscount, gameStock, gameDesc, game_id))        
        db.commit()
        return redirect(url_for("admin"))
    return render_template("updateGame.html", title="Update Game", game=game )

@app.route('/deletegame/<int:game_id>', methods=['GET', 'POST'])
@admin_required
def deletegame(game_id):
    db = get_db()
    game = db.execute("""SELECT * FROM games WHERE game_id = ?;""", (game_id,)).fetchone()
    fileName = game["image"]
    if request.method == "GET":
        file_path = os.path.join(uploadFolder, fileName)
        if os.path.exists(file_path):
            os.remove(file_path)
        db.execute("""DELETE FROM games WHERE game_id = ?;""", (game_id,))        
        db.commit()
    return redirect(url_for("admin"))

@app.route('/addtocart/<int:game_id>', methods=['GET', 'POST'])
def addtocart(game_id):
        if "cart" not in session:
            session["cart"] = {}
        if game_id not in session["cart"]:
            session["cart"][game_id] = 1
        else:
            session["cart"][game_id] = session["cart"][game_id] + 1
        return redirect(url_for("index"))

@app.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
        if "cart" not in session:
            session["cart"] = {}
        names = {}
        prices = {}
        db = get_db()
        totalPrice = 0
        for game_id in session["cart"]:
            game = db.execute("""SELECT * FROM games WHERE game_id = ?;""", (game_id,)).fetchone()
            name = game["name"]
            price = game["price"]
            names[game_id] = name
            prices[game_id] = price
            totalPrice += int(price) * session["cart"][game_id]
        return render_template("cart.html", cart=session["cart"], names=names, prices=prices, totalPrice=totalPrice)

@app.route('/deletefromcart/<int:game_id>', methods=['GET', 'POST'])
def deletefromcart(game_id):
        del session["cart"][game_id]
        return redirect(url_for("cart"))