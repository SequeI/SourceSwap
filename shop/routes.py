from flask import render_template, session, redirect, request, url_for
from shop import app, db

@app.route("/")
def home():
    return "initial setup"