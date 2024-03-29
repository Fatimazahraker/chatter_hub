#!/usr/bin/env python3

import secrets
import os
from time import localtime, strftime
from flask import Flask,  current_app, flash, render_template, request, redirect, url_for
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
from werkzeug.utils import secure_filename
import base64
import binascii


os.environ["DB_USERNAME"] = "chatapp"
os.environ["DB_PASSWORD"] = "noor"
os.environ["DB_NAME"] = "chatapp"
os.environ["DB_EMAIL"] = "eza90782@gmail.com"
os.environ["DB_EMAIL_PASSWD"] = "qzjq vsmg fcyj hipb"


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

    logout_user()
    flash('You have logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/get_rooms', methods=['GET'])
def get_rooms():
    rooms = Room.query.all()
    room_names = [room.name for room in rooms]
    return jsonify({'rooms': room_names})

@app.route('/get_messages/<room>', methods=['GET'])
def get_messages(room):
    print(f"Received request for messages in room: {room}")
    room_obj = Room.query.filter(Room.name.ilike(room)).first()
    if not room_obj:
        abort(404)  # Room not found

    messages = Message.query.filter_by(room_id=room_obj.id).order_by(Message.timestamp).all()
    messages_data = []

    for message in messages:
        image_data = message.image
        if image_data:
            image_data = base64.b64decode(image_data).decode('utf-8')
        message_data = {
            'msg': message.content,
            'username': message.author.username,
            'time_stamp': message.timestamp,
            'image': image_data
        }

        messages_data.append(message_data)

    return jsonify({'messages': messages_data})

   


@app.route("/chat", methods=['GET', 'POST'])
def chat():
 
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    rooms = Room.query.all()
#room = Room.query.filter(Room.name.ilike(room_name)).first()
   # print(f"the room: {room.name}, room id :{room.id}")

    messages = Message.query.order_by(Message.timestamp).all()

    # Printing messages
    print("\nMessages:")
    for message in messages:
        print(f"Message ID: {message.id}, Content: {message.content}, User ID: {message.user_id}, Room ID: {message.room_id}, Timestamp: {message.timestamp}")

    return render_template("chat.html", username=current_user.username, rooms=rooms)

@app.route("/delete_room/<room_name>", methods=['POST'])
@login_required
def delete_room(room_name):
    room = Room.query.filter_by(name=room_name).first()
    if not room or room.created_by != current_user.id:
        abort(403)  # Forbidden - user did not create the room

    # Delete the room and its associated messages
    Message.query.filter_by(room_id=room.id).delete()
    db.session.delete(room)
    db.session.commit()

    return redirect(url_for('chat'))

    
@socketio.on('message')
def message(data):
    user_id = current_user.id if current_user.is_authenticated else None
    roomi = Room.query.filter(Room.name.ilike(data['room'])).first()
    print(data)

    if data['msg'] is None:
        return

    if 'image' in data:
        image_data = base64.b64encode(data['image'].encode('utf-8'))
    else:
        image_data = None
    new_message = Message(content=data['msg'], user_id=user_id, room_id=roomi.id, image=image_data)

    db.session.add(new_message)
    db.session.commit()

    send({
        'msg': data['msg'],
        'username': data['username'],
        #'profile': data['profile'],
        'time_stamp': strftime('%X %x', localtime()),
        'image': data['image'] if 'image' in data else None
    }, room=data['room'])




@socketio.on('join')
def join(data):
    room = data['room']
    join_room(room)
    
    # Send a system message indicating the user has joined
    send({'msg': data['username'] + " has joined the " + room + " room."}, room=room)


@socketio.on('new_room')
def new_room(data):
    room_name = data.get("new_room_name", "").strip()  # Get room name from data and remove leading/trailing spaces

    # Check if the room name is empty
    if not room_name:
        emit('new room error', {'message': 'Room name cannot be empty'})
        return

    # Check if the room already exists in the database
    existing_room = Room.query.filter(Room.name.ilike(room_name)).first()
    if existing_room:
        emit('new room error', {'message': 'Room already exists'})
        return

    # Create a new Room object
    new_room = Room(name=room_name, created_by=current_user.id)
    db.session.add(new_room)
    db.session.commit()

    # Join the new room
    join_room(new_room.name)

    # Emit an event to inform clients about the new room
    emit('new room received', {'new_room_name': new_room.name, 'created_by': new_room.created_by}, broadcast=True)

@socketio.on('delete_room')
def delete_room(data):
    room_name = data['room_name'].strip()
    room = Room.query.filter(Room.name.ilike(room_name)).first()

    if room and room.created_by == current_user.id:
        Message.query.filter_by(room_id=room.id).delete()
        db.session.delete(room)
        db.session.commit()

        # Broadcast the deletion event to inform clients
        emit('room_deleted', {'room_name': room_name}, broadcast=True)
    else:
        emit('delete_room_error', {'message': 'You can\'t delete this room. Only the admin has access'})
        



@socketio.on('leave')
def leave(data):
  
    leave_room(data['room'])
    send({'msg': data['username'] + " has left the " + data['room'] + " room."}, room=data['room'])


if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000, host='0.0.0.0') 