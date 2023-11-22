#!/usr/bin/python3
"""Flask application"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from models import db, User
import os

app = Flask(__name__)
CORS(app)

db_username = os.environ.get('DB_USERNAME', 'default_username')
db_password = os.environ.get('DB_PASSWORD', 'default_password')
db_name = os.environ.get('DB_NAME', 'default_database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_username}:{db_password}@localhost/{db_name}'
db.init_app(app)

@app.route("/", methods=['GET', 'POST'])
def signup():
    """Registration page"""
    try:
        if request.method == 'POST':
            client_side_errors_flag = request.form.get('clientSideErrorsFlag')

            if not client_side_errors_flag or client_side_errors_flag.lower() != 'true':
                username = request.form.get('Username')
                password = request.form.get('password')

                app.logger.info(f"Received form data - Username: {username}, Password: {password}")

                existing_user = User.query.filter_by(username=username).first()

                if existing_user:
                    app.logger.info("User already exists")
                    return jsonify({"status": "user_exists"})

                new_user = User(username=username, password=password)
                db.session.add(new_user)
                db.session.commit()

                app.logger.info("User registration successful")
                return jsonify({"status": "success"})

    except Exception as e:
        app.logger.error(f"An exception occurred: {str(e)}")
        return jsonify({"status": "error"})

    return render_template("signup.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5000', debug=True)
