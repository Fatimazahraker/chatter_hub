from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(60), unique=True, nullable=False)
    verification_token = db.Column(db.String(150), unique=True, nullable=False)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    password = db.Column(db.String(), nullable=False)
    messages = db.relationship('Message', backref='author', lazy=True)
    rooms_created = db.relationship('Room', backref='created_by_user', lazy=True)
    
    def __init__(self, username, password, email, verification_token, is_verified, *arg, **kwarg):
            self.username = username
            self.email = email
            self.verification_token = verification_token
            self.is_verified = is_verified
            self.set_password(password)
        
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Room(db.Model):
    __tablename__ = "rooms"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_rooms', lazy=True)

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    image_path = db.Column(db.String(255))  # Add this line to include the image path