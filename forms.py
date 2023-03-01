from flask_wtf import FlaskForm
from wtforms import  StringField, PasswordField, SubmitField, TextAreaField, IntegerField, FileField
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

class AddGameForm(FlaskForm):
    gameName = StringField("name", [DataRequired()])
    gamePrice = IntegerField("Price", [DataRequired()])
    gameDiscount = IntegerField("Discount", default = 0)
    codeStock = IntegerField("Stock", [DataRequired()])
    gameDesc = TextAreaField("Game Description", [DataRequired])
    gameImage = FileField("Game Picture",[DataRequired] )


