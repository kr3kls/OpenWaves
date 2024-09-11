from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=["POST"])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if user and check_password_hash(user.password, password):
        # if the above check passes, then we know the user has the right credentials
        login_user(user)

        if current_user.role == 2:
            return redirect(url_for('main.ve_account'))
        return redirect(url_for('main.profile'))
    
    # if the above check did not pass, we have an issue
    flash('Please check your login details and try again.')
    return redirect(url_for('auth.login')) 

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=["POST"])
def signup_post():
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
    if user_exists:
        flash("Error 42, Please contact a VE.", "danger") # Intentionally vague error message for security
        return redirect(url_for("auth.signup"))

    # Hash the password
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

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

# VE signup route
@auth.route('/ve_signup', methods=['GET', 'POST'])
@login_required
def ve_signup():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Basic validation
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for("auth.ve_signup"))

        # Check if the username already exists
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash("Error 42, Please contact a VE.", "danger") # Intentionally vague error message for security
            return redirect(url_for("auth.ve_signup"))

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        # Create a new VE account (role 2)
        ve_user = User(
            email=current_user.email,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            username=username,
            password=hashed_password,
            role=2  # Set role to 2 (VE account)
        )
        
        db.session.add(ve_user)
        db.session.commit()
        
        flash('VE account created successfully!', 'success')
        return redirect(url_for('main.ve_account'))

    return render_template('ve_signup.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))
