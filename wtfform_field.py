import secrets
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError, DataRequired, Email

from models import User


class RegistrationForm(FlaskForm):

    username = StringField('Username', validators=[InputRequired(message="Username required"), Length(min=4, max=25, message="Username must be between 4 and 25 characters")])
    email = StringField('email', validators=[InputRequired(message="Email required"), Email(message="Invalid email address")])
    password = PasswordField('Password', validators=[InputRequired(message="Password required"), Length(min=4, max=25, message="Password must be between 4 and 25 characters")])
    firm_pswd = PasswordField('Retype Password', validators=[InputRequired(message="Password required"), EqualTo('password', message="Passwords must match")])

    def validate_username(self, username):
        user_object = User.query.filter_by(username=username.data).first()
        if user_object:
            raise ValidationError("Username already exists. Select a different username.")

    def validate_email(self, email):
        email_object = User.query.filter_by(email=email.data).first()
        if email_object:
            raise ValidationError("email already exists. Select a different email.")
        
    def register_user(self):
        username = self.username.data
        password = self.password.data
        email = self.email.data

        # Generate a verification token
        verification_token = secrets.token_urlsafe(16)

        # Create user object (without adding to the database yet)
        user = User(username=username, password=password, email=email, is_verified=False, verification_token=verification_token)

        return user


class LoginForm(FlaskForm):

    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remenber_me')
    submit = SubmitField('login')
