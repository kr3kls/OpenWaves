"""File: main.py

    This file contains the main routes and view functions for the application.
"""

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .models import User

main = Blueprint('main', __name__)

# Default Route
@main.route('/')
def index():
    """Render the index (home) page of the application.

    Returns:
        Response: The rendered 'index.html' template.
    """
    return render_template('index.html')

# User Profile
@main.route('/profile')
@login_required
def profile():
    """Render the user's profile page.

    This view requires the user to be logged in.

    Returns:
        Response: The rendered 'profile.html' template.
    """
    return render_template('profile.html')

# Route to check for VE account
@main.route('/ve_account')
@login_required
def ve_account():
    """Display the VE (Volunteer Examiner) account page or redirect to VE signup.

    Checks if a VE account associated with the current user's email exists.
    If it does, renders the VE profile page.
    If not, redirects to the VE signup page.

    Returns:
        Response: The rendered 've_profile.html' template or a redirect to VE signup.
    """
    # Query for the VE account using the current user's email and role 2
    ve_user = User.query.filter_by(email=current_user.email, role=2).first()

    if ve_user:
        # If a VE account exists, redirect to the VE profile page
        return render_template('ve_profile.html', ve_user=ve_user)

    # If no VE account exists, redirect to the VE signup page
    return redirect(url_for('auth.ve_signup'))

# Route to handle CSP violations
@main.route('/csp-violation-report-endpoint', methods=['POST'])
def csp_violation_report():
    """Handle incoming CSP violation reports.

    Processes the Content Security Policy (CSP) violation reports sent by the browser.
    Logs the violation details for further analysis.

    Returns:
        Tuple[str, int]: An empty response with HTTP status code 204 (No Content).
    """
    if request.is_json:
        violation_report = request.get_json()
        print("CSP Violation:", violation_report)
    else:
        print("Received non-JSON CSP violation report")
    return '', 204  # Return 204 No Content
