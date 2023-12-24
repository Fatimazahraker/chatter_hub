import secrets
import os
from time import localtime, strftime
from flask import Flask, flash, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from wtforms import ValidationError
from flask_login import current_user, login_user, LoginManager, logout_user, login_required
from verification import sendmail
from wtfform_field import RegistrationForm, LoginForm
from models import *
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_migrate import Migrate
from datetime import datetime
from flask import abort
from flask import jsonify

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
migrate = Migrate(app, db)
socketio = SocketIO(app)

ROOMS = ["lounge", "news", "games", "coding"]
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/verify/<receiver_email>/<receiver_token>', methods=['GET'])
def verify_email_token(receiver_email, receiver_token):
    user = User.query.filter_by(verification_token=receiver_token).first()
    if not user or user.email != receiver_email:
        abort(404)  # User not found or email mismatch
    user.is_verified = True
    db.session.commit()

    return render_template('status.html')

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
        # Attempt to register user
        try:
            user = reg_form.register_user()
            # Send a verification email
            verification_link = url_for('verify_email_token', receiver_email=user.email, receiver_token=user.verification_token, _external=True)
            subject = 'Email Verification'
            html_email = f"Welcome to CHATTER-HUB! Click the following link to verify your email: {verification_link}"
            # Add the user to the database
            db.session.add(user)
            db.session.commit()
            # Send verification email
            sendmail(subject, html_email, user.email)
            # Redirect to a page indicating the verification email has been sent
            return render_template('verification_send.html', email=user.email)
        except ValidationError as e:
            flash(str(e), 'error')
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
        return redirect(url_for('chat', room_name='sport'))
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

@app.route('/get_rooms', methods=['GET'])
def get_rooms():
    rooms = Room.query.all()
    room_names = [room.name for room in rooms]
    return jsonify({'rooms': room_names})

@app.route("/chat", methods=['GET', 'POST'])
@app.route("/chat/<room_name>", methods=['GET', 'POST'])
def chat(room_name='sport'):
    """
    Handles the chat page.

    Returns:
    - GET: Renders the chat page if the user is authenticated, otherwise redirects to the login page.
    - POST: Not used in the current implementation.
    """
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    rooms = Room.query.all()
    room = Room.query.filter(Room.name.ilike(room_name)).first()
    print(f"the room: {room.name}, room id :{room.id}")

    messages = Message.query.filter_by(room_id=room.id).order_by(Message.timestamp).all()

    # Printing messages
    print("\nMessages:")
    for message in messages:
        print(f"Message ID: {message.id}, Content: {message.content}, User ID: {message.user_id}, Room ID: {message.room_id}, Timestamp: {message.timestamp}")

    return render_template("chat.html", username=current_user.username, messages=messages, rooms=rooms)


@socketio.on('message')
def message(data):
    """
    Handles incoming chat messages from users.

    Args:
    - data (dict): Dictionary containing message details (msg, username, room).

    Emits:
    - Sends the message to the specified chat room with additional details.
    """
    user_id = current_user.id if current_user.is_authenticated else None
    print(data)
    print(f"room: {data['room']}")
    # Check if the room exists
    room = Room.query.filter(Room.name.ilike(data['room'])).first()

    print(f"Room ID: {room.id}, Name: {room.name}, Created by: {room.created_by}")

    print(f"message: {data['msg']}")

    # Create a new Message object for a regular user message
    new_message = Message(content=data['msg'], user_id=user_id, room_id=room.id, emoji=data.get('emoji', None))
    print(f"Content: {new_message.content}, User ID: {new_message.user_id}, Room ID: {new_message.room_id}")
    db.session.add(new_message)
    db.session.commit()

    # Broadcast the message to everyone in the room, including the sender
    emit('message', {'msg': data['msg'], 'username': data['username'], 'emoji': data.get('emoji'), 'time_stamp': strftime('%X %x', localtime())}, room=room.name)




@socketio.on('join')
def join(data):
    room = data['room']
    join_room(room)

    # Send a system message indicating the user has joined
    send({'msg': data['username'] + " has joined the " + room + " room."}, room=room)


@socketio.on('new_room')
def new_room(data):
    room_name = data["new_room_name"]
    existing_room = Room.query.filter_by(name=room_name).first()
    if not existing_room:
        # Create a new Room object
        new_room = Room(name=room_name, created_by=current_user.id)
        db.session.add(new_room)

        db.session.commit()

        # Join the new room
        join_room(new_room.name)

        # Emit an event to inform clients about the new room
        emit('new room received', {'new_room_name': new_room.name, 'created_by': new_room.created_by}, broadcast=True)



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