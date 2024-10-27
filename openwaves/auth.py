"""File: auth.py

    This file contains the user authorization methods for the application.
"""

import secrets
import string
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .imports import User, update_user_password, db

auth = Blueprint('auth', __name__)

PAGE_ACCOUNT = 'main.profile'
PAGE_VE_PROFILE = 'main_ve.ve_profile'
PAGE_LOGIN = 'auth.login'
PAGE_LOGOUT = 'auth.logout'
PASS_ENCRYPTION = 'pbkdf2:sha256'
MSG_ACCESS_DENIED = 'Access denied.'

# Route to display login page
@auth.route('/login')
def login():
    """Render the login page.

    Returns:
        Response: The rendered login template.
    """
    return render_template('login.html')

# Route to process login form submission
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

    user = User.query.filter_by(username=username.upper(), active=True).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the
    # database
    if user and check_password_hash(user.password, password):
        # if the above check passes, then we know the user has the right credentials
        login_user(user)

        if current_user.role == 2:
            return redirect(url_for(PAGE_VE_PROFILE))
        return redirect(url_for('main.profile'))

    # if the above check did not pass, we have an issue
    flash('Please check your login details and try again.')
    return redirect(url_for(PAGE_LOGIN))

# Route to display signup page
@auth.route('/signup')
def signup():
    """Render the signup page for new users.

    Returns:
        Response: The rendered signup template.
    """
    return render_template('signup.html')

# Route to process signup form submission
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
    hashed_password = generate_password_hash(password, method=PASS_ENCRYPTION)

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

# Route to display VE signup page
@auth.route('/ve_signup')
def ve_signup():
    """Render the VE signup page.

    If the request method is POST, processes the form data to create a new VE
    (Volunteer Examiner) account. Validates input, checks for existing usernames,
    hashes the password, and adds the new VE user to the database.

    Returns:
        Response: A redirect to the VE account page if successful, or back to the
        VE signup page with an error message if there is a problem.
    """
    return render_template('ve_signup.html')

# Route to process VE signup form submission
@auth.route('/ve_signup', methods=['POST'])
def ve_signup_post():
    """Process VE account creation.

    Processes the form data to create a new VE
    (Volunteer Examiner) account. Validates input, checks for existing usernames,
    hashes the password, and adds the new VE user to the database.

    Returns:
        Response: A redirect to the VE account page if successful, or back to the
        VE signup page with an error message if there is a problem.
    """
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
    user_exists = User.query.filter_by(username=username.upper()).first()
    if user_exists:
        flash("Error 42, Please contact the Lead VE.", "danger") # Intentionally vague error message
        return redirect(url_for("auth.ve_signup"))

    # Hash the password
    hashed_password = generate_password_hash(password, method=PASS_ENCRYPTION)

    # Check if a VE Account already exists
    ve_user_exists = User.query.filter_by(role=2).first()

    if not ve_user_exists:
        # Create a new VE account (role 2) with active set to True
        ve_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            username=username.upper(),
            password=hashed_password,
            role=2,  # Set role to 2 (VE account)
            active=True  # Set active to True (This is the first VE Account)
        )
    else:
        # Create a new VE account (role 2)
        ve_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            username=username.upper(),
            password=hashed_password,
            role=2,  # Set role to 2 (VE account)
            active=False  # Set active to False (must be approved by an existing VE)
        )

    db.session.add(ve_user)
    db.session.commit()

    flash(f'VE account for {username} created successfully!', 'success')
    return redirect(url_for(PAGE_LOGIN))

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
    if current_user.role in [1, 2]:
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
        return redirect(url_for(PAGE_VE_PROFILE))
    return redirect(url_for(PAGE_LOGOUT))

@auth.route('/ve_management')
@login_required
def ve_management():
    """Handle management of VE accounts."""
    if current_user.role != 2:  # Allow only VE users (role 2) to access this page
        flash("Access denied.", "danger")
        return redirect(url_for(PAGE_LOGOUT))

    ve_accounts = User.query.filter(User.role == 2).all()  # Query to fetch all VE accounts
    return render_template('ve_management.html', ve_accounts=ve_accounts)

@auth.route('/toggle_account_status/<int:account_id>', methods=['POST'])
@login_required
def toggle_account_status(account_id):
    """
    Toggles the active status of a user account.

    This route is restricted to users with a VE role (role 2) and allows them to
    change the active/inactive status of another user account. If the current user
    does not have the necessary permissions, they are logged out. If the target
    account is not found, an error is flashed to the user.

    Args:
        account_id (int): The ID of the account to toggle the status of.

    Returns:
        Response: A redirection to the VE management page with a success or error 
        message flashed to the user.
    """
    if current_user.role != 2:  # Only VE users can change status
        flash("Access denied.", "danger")
        return redirect(url_for(PAGE_LOGOUT))

    account = db.session.get(User, account_id)
    if not account:
        flash("Account not found.", "danger")
        return redirect(url_for('auth.ve_management'))

    # Toggle active status
    account.active = not account.active
    db.session.commit()
    flash(f"Account status updated to {'active' if account.active else 'disabled'}.", "success")
    return redirect(url_for('auth.ve_management'))

@auth.route('/password_resets')
@login_required
def password_resets():
    """
    Displays the password reset management page for VE users.

    Returns:
        Response: Rendered HTML page showing a list of accounts and the option to reset passwords.
    """
    if current_user.role != 2:  # Only VE users can view this page
        flash("Access denied.", "danger")
        return redirect(url_for(PAGE_LOGOUT))

    accounts = User.query.all()  # Fetch all user accounts
    return render_template('password_resets.html', accounts=accounts)

@auth.route('/reset_password/<int:account_id>', methods=['POST'])
@login_required
def reset_password(account_id):
    """
    Resets the password of a user account to a secure 8-character string and flashes
    it to the VE user.

    Args:
        account_id (int): The ID of the account whose password is being reset.

    Returns:
        Response: Redirects to the password reset page with a flash message showing
        the new password.
    """
    print("Password reset requested")
    if current_user.role != 2:  # Only VE users can reset passwords
        flash("Access denied.", "danger")
        return redirect(url_for(PAGE_LOGOUT))

    account = db.session.get(User, account_id)
    if not account:
        flash("Account not found.", "danger")
        return redirect(url_for('auth.password_resets'))

    # Generate a secure 8-character password (upper, lower, digits)
    alphabet = string.ascii_letters + string.digits  # Uppercase, lowercase, and digits
    new_password = ''.join(secrets.choice(alphabet) for _ in range(8))

    # Update the account's password
    account.password = generate_password_hash(new_password, method=PASS_ENCRYPTION)
    db.session.commit()

    flash(f"Password for {account.username} has been reset. " +
          f"New password: {new_password}", "success")
    return redirect(url_for('auth.password_resets'))

@auth.route('/logout')
@login_required
def logout():
    """Log out the current user and redirect to the login page.

    Returns:
        Response: A redirect to the login page after logging out.
    """
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for(PAGE_LOGIN))
