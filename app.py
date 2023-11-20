#!/usr/bin/python3
""" flask application"""
from flask import Flask, render_template
import os
from models import db, User

db_username = os.environ.get('DB_USERNAME', 'default_username')
db_password = os.environ.get('DB_PASSWORD', 'default_password')
db_name = os.environ.get('DB_NAME', 'default_database')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_username}:{db_password}@localhost/{db_name}'
db.init_app(app)


@app.route("/", methods=['GET', 'POST'])
def signup():
    "registration page"
    
    return render_template("signup.html")

if __name__ == "__main__":
    """main function"""
    app.run(host='0.0.0.0', port='5000', debug=True)
