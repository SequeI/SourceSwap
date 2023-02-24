from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///gameshop.db"
db = SQLAlchemy(app)
app.config["SECRET_KEY"] = "2345235"

from shop.admin import route
