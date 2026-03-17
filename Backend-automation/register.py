import os

from flask import Flask, redirect, render_template, request, session, url_for
from Form import RegistrationForm
from model.user import db
import bcrypt
import pymysql
pymysql.install_as_MySQLdb()
from model.user import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:%23Alan123@localhost:3306/full_stack'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_url = os.environ.get("DATABASE_URL", "mysql://root:@localhost:3306/full_stack")

if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = db_url


# db.init_app(app)
# with app.app_context():
#     db.create_all()
    # print("Database tables created successfully.")
@app.route('/register',methods=["GET","POST"])
def register():
    form = RegistrationForm()
    if request.method == "POST" and form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()
        
        if existing_user:
            return render_template("register.html", form=form, message="Username already exists. Please choose a different username.")
        if existing_email:
            return render_template("register.html", form=form, message="Email already registered. Please use a different email.")

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return render_template(
            "login.html",
            message=f"Registration successful for user {username}! Please log in.",
        )  
    return render_template("register.html", form=form)
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        # encode only the supplied password for comparison
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            session['username'] = username
            return redirect(url_for('dashboard', username=username))
        else:
            return "Invalid username or password. Please try again."
    return render_template("login.html")
@app.route('/delete_account', methods=["POST"])
def delete_account():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=username).first()
    if user:
        db.session.delete(user)
        db.session.commit()
    session.pop('username', None)
    return redirect(url_for('login'))
@app.route('/update_email', methods=["POST"])
def update_email():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    new_email = request.form.get('new_email')
    if not new_email:
        return redirect(url_for('dashboard', username=username))
    existing = User.query.filter_by(email=new_email).first()
    if existing and existing.username != username:
        return redirect(url_for('dashboard', username=username))
    user = User.query.filter_by(username=username).first()
    if user:
        user.email = new_email
        db.session.commit()
    return redirect(url_for('dashboard', username=username))
@app.route('/read', methods=["POST"])
def read():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=username).first()
    if user:
        return f"Username: {user.username}, Email: {user.email}"
    return "User not found."
@app.route('/create_user', methods=["POST"])
def create_user():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    if not username or not email or not password:
        return "All fields are required."
    existing_user = User.query.filter_by(username=username).first()
    existing_email = User.query.filter_by(email=email).first()
    if existing_user:
        return "Username already exists. Please choose a different username."
    if existing_email:
        return "Email already registered. Please use a different email."
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return f"User {username} created successfully."
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))
 
@app.route('/dashboard/<username>')
def dashboard(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('login'))
    return render_template("dashboard.html",username=username)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
