from flask_wtf import FlaskForm
from wtforms import  StringField, PasswordField, SubmitField
from wtforms.validators import Length, DataRequired, EqualTo

class RegistrationForm(FlaskForm):
    name = StringField('Name', [Length(min=4, max=25)])
    username = StringField('Username', [Length(min=4, max=25)])
    email = StringField('Email Address', [Length(min=6, max=35)])
    password = PasswordField('New Password', [
        DataRequired(),
        EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    email = StringField('Email Address', [Length(min=6, max=35)])
    password = PasswordField('Password', [DataRequired()])
    submit = SubmitField("Submit")

