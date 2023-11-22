import secrets
import os
from flask import Flask, flash, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, login_user, LoginManager
from wtfform_field import*
from models import db, User


db_username = os.environ.get('DB_USERNAME', 'default_username')
db_password = os.environ.get('DB_PASSWORD', 'default_password')
db_name = os.environ.get('DB_NAME', 'default_database')

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_username}:{db_password}@localhost:5432/{db_name}'

db.init_app(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route("/", methods=['GET', 'POST'])
def index():
    reg_form = RegistrationForm()

    if reg_form.validate_on_submit():
        username = reg_form.username.data
        password = reg_form.password.data

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("index.html", form=reg_form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('login'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.password == form.password.data:
            flash('invalid username or password')
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        return ("success")
    return render_template('login.html', title='Sign In', form=form)
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
