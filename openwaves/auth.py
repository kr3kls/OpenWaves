"""File: auth.py

    This file contains the user authorization methods for the application.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from .utils import update_user_password
from . import db

auth = Blueprint('auth', __name__)

PAGE_ACCOUNT = 'main.profile'
PAGE_VE_ACCOUNT = 'main.ve_account'

@auth.route('/login')
def login():
    """Render the login page.

    Returns:
        Response: The rendered login template.
    """
    return render_template('login.html')

@auth.route('/login', methods=["POST"])
def login_post():
    """Process the login form submission.

    Retrieves the username and password from the form, verifies the credentials,
    logs in the user if successful, and redirects to the appropriate page based
    on the user's role.

    Returns:
        Response: A redirect to the profile page if successful, or back to the
        login page with an error message if authentication fails.
    """
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the
    # database
    if user and check_password_hash(user.password, password):
        # if the above check passes, then we know the user has the right credentials
        login_user(user)

        if current_user.role == 2:
            return redirect(url_for(PAGE_VE_ACCOUNT))
        return redirect(url_for('main.profile'))

    # if the above check did not pass, we have an issue
    flash('Please check your login details and try again.')
    return redirect(url_for('auth.login'))

@auth.route('/signup')
def signup():
    """Render the signup page for new users.

    Returns:
        Response: The rendered signup template.
    """
    return render_template('signup.html')

@auth.route('/signup', methods=["POST"])
def signup_post():
    """Process the signup form submission.

    Collects user information from the form, validates input, checks for
    existing users, hashes the password, creates a new user record, and adds
    it to the database.

    Returns:
        Response: A redirect to the login page if successful, or back to the
        signup page with an error message if there is a problem.
    """
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
        flash("Error 42, Please contact a VE.", "danger") # Intentionally vague error message
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

# Route to update user profiles
@auth.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    """Handle the form submission to update the user's profile.

    Retrieves data from the form, updates the current user's information,
    updates the password if provided and confirmed, commits changes to the database,
    and redirects back to the profile page with a success message.

    Returns:
        Response: A redirect to the profile page.
    """
    username = request.form.get('username')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    # Update user data
    current_user.username = username
    current_user.first_name = first_name
    current_user.last_name = last_name
    current_user.email = email

    # Update password if provided and confirmed
    if password and password == confirm_password:
        update_user_password(current_user, password)

    db.session.commit()

    flash('Profile updated successfully!', 'success')
    if current_user.role == 1:
        return redirect(url_for(PAGE_ACCOUNT))
    if current_user.role == 2:
        return redirect(url_for(PAGE_VE_ACCOUNT))
    return redirect(url_for('auth.logout'))

# VE signup route
@auth.route('/ve_signup', methods=['GET', 'POST'])
def ve_signup():
    """Render the VE signup page and process VE account creation.

    If the request method is POST, processes the form data to create a new VE
    (Volunteer Examiner) account. Validates input, checks for existing usernames,
    hashes the password, and adds the new VE user to the database.

    Returns:
        Response: A redirect to the VE account page if successful, or back to the
        VE signup page with an error message if there is a problem.
    """
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Basic validation
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for("auth.ve_signup"))

        # Check if the username already exists
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash("Error 42, Please contact a VE.", "danger") # Intentionally vague error message
            return redirect(url_for("auth.ve_signup"))

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        # Create a new VE account (role 2)
        ve_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=hashed_password,
            role=2  # Set role to 2 (VE account)
        )

        db.session.add(ve_user)
        db.session.commit()

        flash('VE account created successfully!', 'success')
        return redirect(url_for(PAGE_VE_ACCOUNT))

    return render_template('ve_signup.html')

@auth.route('/logout')
@login_required
def logout():
    """Log out the current user and redirect to the login page.

    Returns:
        Response: A redirect to the login page after logging out.
    """
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))

if __name__ == "__main__":
    pass
