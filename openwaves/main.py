"""File: main.py

    This file contains the main routes and view functions for the application.
"""

import csv
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from io import TextIOWrapper
from werkzeug.utils import secure_filename
from .imports import db, Pool, Question

main = Blueprint('main', __name__)

# Default Route
@main.route('/')
def index():
    """Render the index (home) page of the application.

    Returns:
        Response: The rendered 'index.html' template.
    """
    return render_template('index.html')

# Default Route
@main.route('/account_select')
def account_select():
    """Render the account select page of the application.

    Returns:
        Response: The rendered 'account_select.html' template.
    """
    return render_template('account_select.html')

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

    Checks if the current user is a VE account.
    If it is, renders the VE profile page.
    If not, redirects to logout.

    Returns:
        Response: The rendered 've_profile.html' template or a redirect to logout.
    """
    # Check if the current user has role 2
    if current_user.role == 2:
        # If a VE account exists, redirect to the VE profile page
        return render_template('ve_profile.html', ve_user=current_user)

    # If no VE account exists, redirect to the logout page
    return redirect(url_for('auth.logout'))

# Route to show pools page
@main.route('/pools')
@login_required
def pools():
    """Render the pools page of the application.

    Returns:
        Response: The rendered 'pools.html' template.
    """
    # Get all question pools from the database
    question_pools = Pool.query.all()
    for question_pool in question_pools:
        question_count = Question.query.filter_by(pool_id=question_pool.id).count()
        question_pool.question_count = question_count
    return render_template('pools.html', question_pools=question_pools)

# Route to create question pools
@main.route('/create_pool', methods=['POST'])
@login_required
def create_pool():
    """
    Creates a new question pool and stores it in the database.

    This route handles the creation of a question pool by accepting form data
    through a POST request. The form data should include the pool name, exam element,
    start date, and end date. If any of the required fields are missing, a 400 error 
    is returned with a message indicating that all fields are required.

    On successful creation of the question pool, the pool is added to the database
    and a JSON response with success status is returned.

    Returns:
        Response: A JSON response with a success message and a 200 status code on
        successful creation, or a 400 status code with an error message if any field
        is missing.
    """

    # Get the form data
    pool_name = request.form.get('pool_name')
    exam_element = request.form.get('exam_element')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    # Validate the form data
    if not pool_name or not exam_element or not start_date or not end_date:
        return jsonify({"error": "All fields are required."}), 400

    # Create a new question pool entry in the database
    new_pool = Pool(
        name=pool_name,
        element=exam_element,
        start_date=datetime.strptime(start_date, '%Y-%m-%d'),
        end_date=datetime.strptime(end_date, '%Y-%m-%d'),
    )
    db.session.add(new_pool)
    db.session.commit()

    return jsonify({"success": True}), 200

@main.route('/upload_questions/<int:pool_id>', methods=['POST'])
@login_required
def upload_questions(pool_id):
    """Handle the CSV upload for questions and associate them with the given pool_id."""
    file = request.files.get('file')

    if not file:
        return jsonify({"error": "No file provided."}), 400

    filename = secure_filename(file.filename)
    if not filename.endswith('.csv'):
        return jsonify({"error": "Invalid file type. Only CSV files are allowed."}), 400

    # Parse the CSV file
    file_stream = TextIOWrapper(file.stream, encoding='utf-8')
    csv_reader = csv.DictReader(file_stream)

    questions = []
    for row in csv_reader:
        # Assuming the CSV has the fields: id, correct, question, a, b, c, d, refs
        new_question = Question(
            number=row['id'],
            pool_id=pool_id,  # Associate with the correct pool
            correct_answer=row['correct'],
            question=row['question'],
            option_a=row['a'],
            option_b=row['b'],
            option_c=row['c'],
            option_d=row['d'],
            refs=row['refs']
        )
        questions.append(new_question)

    # Add all questions to the database
    db.session.bulk_save_objects(questions)
    db.session.commit()

    return jsonify({"success": True}), 200

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
