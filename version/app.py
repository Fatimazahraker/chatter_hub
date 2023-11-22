from flask import Flask, render_template, request, jsonify
from models import db, User

app = Flask(__name__)

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5000/database'
db.init_app(app)

@app.route("/", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            username = request.form.get('Username')
            password = request.form.get('password')
            firm_password = request.form.get('firm-pswrd')

            # Validate form data
            if not (username and password and password == firm_password):
                return jsonify({"status": "error", "message": "Validation failed"})

            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return jsonify({"status": "error", "message": "User already exists"})

            # Form data is valid, create a new user
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()

            return jsonify({"status": "success", "message": "User registration successful"})

        except Exception as e:
            # Log the exception for debugging
            print(f"An exception occurred: {str(e)}")
            return jsonify({"status": "error", "message": "An error occurred during form submission."})

    return render_template("signup.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

