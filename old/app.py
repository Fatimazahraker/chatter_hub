import secrets
import os
from time import localtime, strftime
from flask import Flask, flash, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, login_user, LoginManager, logout_user, login_required
from wtfform_field import RegistrationForm, LoginForm
from models import *
from flask_socketio import SocketIO, send, emit, join_room, leave_room
"""
A simple Flask application for a chat system with user registration and login features.

Modules:
- secrets: Generate cryptographically strong pseudo-random numbers suitable for managing secrets.
- os: Provides a way of using operating system-dependent functionality.
- time: Provides various time-related functions.
- Flask: A web framework for building web applications in Python.
- flask_sqlalchemy: Flask extension for SQLAlchemy, a SQL toolkit and Object-Relational Mapping (ORM) library.
- flask_login: Flask extension for managing user authentication.
- wtfform_field: Custom form fields (assuming it's a module in your project).
- models: Contains the User model for database interactions.
- flask_socketio: Flask extension for Socket.IO, a real-time communication library.

Routes:
- /: Home page, handles user registration.
- /login: Login page.
- /logout: Logout route.
- /chat: Chat page, requires authentication.

Socket.IO Events:
- message: Handles incoming chat messages.
- join: Handles user joining a chat room.
- leave: Handles user leaving a chat room.
"""

db_username = os.environ.get('DB_USERNAME', 'default_username')
db_password = os.environ.get('DB_PASSWORD', 'default_password')
db_name = os.environ.get('DB_NAME', 'default_database')

app = Flask(__name__)

app.secret_key = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_username}:{db_password}@localhost/{db_name}'

db.init_app(app)
socketio = SocketIO(app)
ROOMS = ["lounge", "news", "games", "coding"]
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def home():
    return render_template('main.html')

@app.route("/index", methods=['GET', 'POST'], strict_slashes=False)
def index():
    """
    Handles the home page for user registration.

    Returns:
    - GET: Renders the registration form.
    - POST: Processes the form data, registers the user, and redirects to the login page.
    """
    reg_form = RegistrationForm()

    if reg_form.validate_on_submit():
        username = reg_form.username.data
        password = reg_form.password.data
        
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Registered successfully. Please login.', 'success')
        return redirect(url_for("login"))
    return render_template("index.html", form=reg_form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    """
    Handles the login page.

    Returns:
    - GET: Renders the login form.
    - POST: Processes the form data, logs in the user, and redirects to the chat page.
    """
    if current_user.is_authenticated:
        return redirect(url_for('login'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('invalid username or password', category='error')
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('chat'))
    return render_template('login.html', title='Sign In', form=form)


@app.route("/logout", methods=['GET'])
def logout():
    """
    Logs out the current user and redirects to the login page.

    Returns:
    - GET: Redirects to the login page after logging out.
    """
    logout_user()
    flash('You have logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route("/chat", methods=['GET', 'POST'])
def chat():
    """
    Handles the chat page.

    Returns:
    - GET: Renders the chat page if the user is authenticated, otherwise redirects to the login page.
    - POST: Not used in the current implementation.
    """
    if not current_user.is_authenticated:
        #flash('Please login', 'danger')
        return redirect(url_for('login'))

    return render_template("chat.html", username=current_user.username, rooms=ROOMS)

@socketio.on('message')
def message(data):
    """
    Handles incoming chat messages from users.

    Args:
    - data (dict): Dictionary containing message details (msg, username, room).

    Emits:
    - Sends the message to the specified chat room with additional details.
    """
    print(f"\n\n {data}\n\n")
    send({'msg': data['msg'], 'username': data['username'], 'time_stamp':
        strftime('%X %x', localtime())}, room=data['room'])

@socketio.on('join')
def join(data):
    """
    Handles a user joining a chat room.

    Args:
    - data (dict): Dictionary containing user and room details.

    Emits:
    - Sends a system message to the chat room indicating the user has joined.
    """
    join_room(data['room'])
    send({'msg': data['username'] + " has joined the " + data['room'] + " room."}, room=data['room'])

@socketio.on('new_room')
def new_room(data):
    room = data["new_room_name"]
    print(room)
    ROOMS.append(room)
    join_room(room)
    emit('new room received', data, broadcast=True)

@socketio.on('leave')
def leave(data):
    """
    Handles a user leaving a chat room.

    Args:
    - data (dict): Dictionary containing user and room details.
    """
    leave_room(data['room'])
    send({'msg': data['username'] + " has left the " + data['room'] + " room."}, room=data['room'])


if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000, host='0.0.0.0')
