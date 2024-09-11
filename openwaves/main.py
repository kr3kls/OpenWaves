from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .utils import update_user_password
from .models import User
from . import db 

main = Blueprint('main', __name__)

# Default Route
@main.route('/')
def index():
    return render_template('index.html')

# User Profile
@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

# Route to update user profiles
@main.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
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
    return redirect(url_for('main.profile'))

# Route to check for VE account
@main.route('/ve_account')
@login_required
def ve_account():
    # Query for the VE account using the current user's email and role 2
    ve_user = User.query.filter_by(email=current_user.email, role=2).first()

    if ve_user:
        # If a VE account exists, redirect to the VE profile page
        return render_template('ve_profile.html', ve_user=ve_user)
    else:
        # If no VE account exists, redirect to the VE signup page
        return redirect(url_for('auth.ve_signup'))

@main.route('/update_ve_account', methods=['POST'])
@login_required
def update_ve_account():
    ve_user = User.query.filter_by(email=current_user.email, role=2).first()

    if not ve_user:
        flash('VE account not found.', 'danger')
        return redirect(url_for('main.ve_account'))

    # Update user data from form
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    # Update VE user details
    ve_user.username = username

    # If password is provided, update it
    if password and password == confirm_password:
        update_user_password(ve_user, password)

    db.session.commit()
    flash('VE account updated successfully!', 'success')
    return redirect(url_for('main.ve_account'))


# Route to handle CSP violations
@main.route('/csp-violation-report-endpoint', methods=['POST'])
def csp_violation_report():
    if request.is_json:
        violation_report = request.get_json()
        print("CSP Violation:", violation_report)
    else:
        print("Received non-JSON CSP violation report")
    return '', 204  # Return 204 No Content
