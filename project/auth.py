from flask import Blueprint, render_template, redirect, url_for, request, flash
from .models import User
from . import db, bcrypt

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=["GET", "POST"])
def login():
    # Here you can add login logic later
    return render_template('login.html')

@auth.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Fetch form data
        username = request.form.get("username")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Basic validation
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for("auth.signup"))

        # Check if the username or email already exists
        user_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()
        if user_exists or email_exists:
            flash("Username or Email already exists", "danger")
            return redirect(url_for("auth.signup"))

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create and add the user
        new_user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_password,
            role=1 # User role 1 is HAM Candidate
        )
        db.session.add(new_user)
        db.session.commit()

        flash(f"Account created for {username}!", "success")
        return redirect(url_for("auth.login"))

    return render_template('signup.html')

@auth.route('/logout')
def logout():
    # TODO Logout logic goes here
    return 'Logout'
