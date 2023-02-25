from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///gameshop.db"
db = SQLAlchemy(app)
app.config["SECRET_KEY"] = "2345235"
bcrypt = Bcrypt(app)

from shop.admin import route
