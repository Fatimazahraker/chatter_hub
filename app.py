#!/usr/bin/python3
""" flask application"""
from flask import Flask, jsonify, render_template, request, redirect, url_for
import os
from models import *
from flask_sqlalchemy import SQLAlchemy

db_username = os.environ.get('DB_USERNAME', 'default_username')
db_password = os.environ.get('DB_PASSWORD', 'default_password')
db_name = os.environ.get('DB_NAME', 'default_database')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_username}:{db_password}@localhost/{db_name}'
db = SQLAlchemy(app)

@app.route("/", methods=['GET', 'POST'])
def signup():
    "registration page"
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        firm_password = request.form['firm_password']
        if not (username and password and firm_password and password == firm_password):
            return jsonify({"error": "Invalid input. Please check your data."}), 400

        exit_user = User.query.filter_by(username=username).first()
        if exit_user:
            return jsonify({"error": "Username already taken. Please choose another one."}), 400

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('success'))
        #return jsonify({"error": "User registered successfully"}), 200
    return render_template("signup.html")

@app.route("/success")
def success():
    return "User registered successfully!"

if __name__ == "__main__":
    """main function"""
    app.run(host='0.0.0.0', port='5000', debug=True)
