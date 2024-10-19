"""File: main.py

    This file contains the main routes and view functions for the application.
"""

import os
import csv
from datetime import datetime
from io import TextIOWrapper
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, \
    current_app as app
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from .imports import db, Pool, Question, TLI, ExamSession, ExamRegistration, get_exam_name, \
    is_already_registered, remove_exam_registration, load_question_pools, allowed_file, \
    ExamDiagram, Exam, ExamAnswer

PAGE_LOGOUT = 'auth.logout'
PAGE_SESSIONS = 'main.sessions'
MSG_ACCESS_DENIED = 'Access denied.'

main = Blueprint('main', __name__)

# Default Route
@main.route('/')
def index():
    """Render the index (home) page of the application.

    Returns:
        Response: The rendered 'index.html' template.
    """
    return render_template('index.html')

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

# Account Select Route
@main.route('/account_select')
def account_select():
    """Render the account select page of the application.

    Returns:
        Response: The rendered 'account_select.html' template.
    """
    return render_template('account_select.html')

#####################################
#                                   #
#     HC (Ham Candidate) Routes     #
#                                   #
#####################################

# User Profile Route
@main.route('/profile')
@login_required
def profile():
    """Render the user's profile page.

    This view requires the user to be logged in.

    Returns:
        Response: The rendered 'profile.html' template.
    """
    if current_user.role == 1:
        # If a HC account exists, render the profile page
        return render_template('profile.html')

    # If no HC account exists, redirect to the logout page
    flash(MSG_ACCESS_DENIED, "danger")
    return redirect(url_for(PAGE_LOGOUT))

# Exam Sessions Route
@main.route('/sessions')
@login_required
def sessions():
    """
    Render the exam sessions page for the logged-in user.

    This route handles the display of exam sessions for HAM candidates (role 1 users), 
    providing information about each session's date, status, and the user's registration 
    for specific exam elements (Tech, General, Extra).

    Args:
        None (the user must be logged in as role 1).

    Returns:
        Response: Renders the 'sessions.html' template, with the following context variables:
        - exam_sessions (list[dict]): A list of exam sessions with user registration details:
            - id (int): The session ID.
            - session_date (datetime): The date of the exam session.
            - start_time (datetime): The start time of the session (if it has started).
            - end_time (datetime): The end time of the session (if it has ended).
            - status (bool): The status of the session (open or closed).
            - tech_registered (bool): Whether the user is registered for the Technician exam.
            - gen_registered (bool): Whether the user is registered for the General exam.
            - extra_registered (bool): Whether the user is registered for the Extra exam.
        - current_date (date): The current date, used in the template for status comparisons.
    """
    if current_user.role == 1:
        # Get all test sessions from the database
        exam_sessions = \
            db.session.query(ExamSession).order_by(ExamSession.session_date.desc()).all()

        # Get the current user's registrations
        user_registrations = \
            db.session.query(ExamRegistration).filter_by(user_id=current_user.id).all()

        # Create a list to pass to the template with registration info
        sessions_with_registrations = []
        for session in exam_sessions:
            # Find if the user is registered for this session and exam elements
            tech_registered = any(reg.session_id == session.id and
                                  reg.tech for reg in user_registrations)
            gen_registered = any(reg.session_id == session.id and
                                 reg.gen for reg in user_registrations)
            extra_registered = any(reg.session_id == session.id and
                                   reg.extra for reg in user_registrations)

            sessions_with_registrations.append({
                'id': session.id,
                'session_date': session.session_date,
                'start_time': session.start_time,
                'end_time': session.end_time,
                'status': session.status,
                'tech_pool_id': session.tech_pool_id,
                'gen_pool_id': session.gen_pool_id,
                'extra_pool_id': session.extra_pool_id,
                'tech_registered': tech_registered,
                'gen_registered': gen_registered,
                'extra_registered': extra_registered
            })

        current_date = datetime.now().date()
        return render_template('sessions.html',
                               exam_sessions=sessions_with_registrations,
                               current_date=current_date)

    # If no HC account exists, redirect to the logout page
    flash(MSG_ACCESS_DENIED, "danger")
    return redirect(url_for(PAGE_LOGOUT))

# Route to register for an exam session
@main.route('/register', methods=['POST'])
@login_required
def register():
    """
    Register a user for a specified exam element in an exam session.

    This method processes a POST request from the registration form, allowing a 
    user with the appropriate role (role 1) to register for an exam element (Tech, 
    General, or Extra) in a selected exam session. If the user is already registered 
    for the selected exam element, it returns an appropriate message. Otherwise, 
    the user's registration is created or updated.

    Args:
        None (input data is taken from the form submission via POST request):
        - session_id (str): The ID of the exam session.
        - exam_element (str): The exam element to register for ('2' = Tech, '3' = General,
          '4' = Extra).

    Returns:
        Redirect to the sessions page with:
        - Success message if registration is successful.
        - Error message if there is invalid input, the session is not found, or the user is already
          registered.
    """
    if current_user.role == 1:
        # Get session ID and exam element from the form
        session_id = request.form.get('session_id')
        exam_element = request.form.get('exam_element')
        exam_name = get_exam_name(exam_element)

        # Check for missing input data
        if not session_id or not exam_element or not exam_name:
            flash('Invalid registration request. Missing required information.', 'danger')
            return redirect(url_for(PAGE_SESSIONS))

        # Fetch exam session
        exam_session = db.session.get(ExamSession, session_id)
        if not exam_session:
            flash('Exam session not found.', 'danger')
            return redirect(url_for(PAGE_SESSIONS))

        # Fetch existing registration
        existing_registration = ExamRegistration.query.filter_by(
            session_id=session_id,
            user_id=current_user.id
        ).first()

        # Check if the user is already registered for this element
        if existing_registration and is_already_registered(existing_registration, exam_element):
            flash(f'You are already registered for the {exam_name} exam.', 'danger')
            return redirect(url_for(PAGE_SESSIONS))

        # Create or update registration
        if existing_registration:
            if exam_element == '2':
                existing_registration.tech = True
            elif exam_element == '3':
                existing_registration.gen = True
            elif exam_element == '4':
                existing_registration.extra = True
        else:
            new_registration = ExamRegistration(
                session_id=session_id,
                user_id=current_user.id,
                tech=(exam_element == '2'),
                gen=(exam_element == '3'),
                extra=(exam_element == '4'),
                valid=False
            )
            db.session.add(new_registration)

        # Commit changes and confirm registration
        db.session.commit()
        flash(f'Successfully registered for the {exam_name} exam.', 'success')
        return redirect(url_for(PAGE_SESSIONS))

    # If no HC account exists, redirect to the logout page
    flash(MSG_ACCESS_DENIED, "danger")
    return redirect(url_for(PAGE_LOGOUT))

# Route to cancel exam registration
@main.route('/cancel_registration', methods=['POST'])
@login_required
def cancel_registration():
    """
    Cancel a user's registration for an exam element in an exam session.

    This method handles the POST request from the form to cancel a user's registration 
    for a specific exam element (Tech, General, Extra) within a session. The user 
    must have a role of 1 (HAM Candidate) to cancel the registration. If the user 
    is not registered for the specified exam element, an appropriate error message 
    is displayed.

    Args:
        None (input data is taken from the form submission via POST request):
        - session_id (str): The ID of the exam session.
        - exam_element (str): The exam element to cancel registration for ('2' = Tech,
          '3' = General, '4' = Extra).

    Returns:
        Redirect to the sessions page with:
        - Success message if cancellation is successful.
        - Error message if input is missing, the session is not found, or the user is not
          registered.
    """
    if current_user.role == 1:
        # Get session ID and exam element from the form data
        session_id = request.form.get('session_id')
        exam_element = request.form.get('exam_element')
        exam_name = get_exam_name(exam_element)  # Reusing the helper function

        # Check for missing input data
        if not session_id or not exam_element or not exam_name:
            flash('Invalid cancellation request. Missing required information.', 'danger')
            return redirect(url_for(PAGE_SESSIONS))

        # Fetch the exam session
        exam_session = db.session.get(ExamSession, session_id)
        if not exam_session:
            flash('Exam session not found.', 'danger')
            return redirect(url_for(PAGE_SESSIONS))

        # Fetch the existing registration
        existing_registration = ExamRegistration.query.filter_by(
            session_id=session_id,
            user_id=current_user.id
        ).first()

        # Check if the user is registered for this exam element
        if not existing_registration or not is_already_registered(existing_registration,
                                                                  exam_element):
            flash(f'You are not registered for the {exam_name} exam.', 'danger')
            return redirect(url_for(PAGE_SESSIONS))

        # Remove the user's registration for the specified exam element
        remove_exam_registration(existing_registration, exam_element)

        # Commit the changes to the database
        db.session.commit()

        # Flash success message and redirect
        flash(f'Successfully canceled registration for the {exam_name} exam.', 'success')
        return redirect(url_for(PAGE_SESSIONS))

    # If no HC account exists, redirect to the logout page
    flash(MSG_ACCESS_DENIED, "danger")
    return redirect(url_for(PAGE_LOGOUT))

@main.route('/launch-exam', methods=['POST'])
@login_required
def launch_exam(): # pylint: disable=R0911
    """
    Start a new exam session for the user.

    This route handles the POST request to initiate an exam session for a user who 
    has registered for a specific exam element (Tech, General, Extra) within an exam session. 
    The user must have a role of 1 (HAM Candidate) to take the exam. The system checks for 
    the validity of the exam session, user registration, and ensures the user has not 
    already started an exam session for the requested exam element. If all conditions are met, 
    a new exam session is created, and 35 questions from the relevant pool are assigned to 
    the user.

    Args:
        None (input data is taken from the form submission via POST request):
        - session_id (str): The ID of the exam session.
        - exam_element (str): The exam element to be taken ('tech' = Technician, 
          'gen' = General, 'extra' = Extra).

    Returns:
        Redirect:
        - If successful, redirects to the 'take_exam' route for the user to begin the exam.
        - If the session is not found, input data is missing, or the user is not registered 
          for the requested exam element, an error message is flashed, and the user is 
          redirected to the sessions page.
        - If the user has already started the exam for the requested element, they are redirected 
          to the existing exam session.
        - In case of any database or server errors, a generic error message is flashed, and the 
          user is redirected to the sessions page.

    Raises:
        SQLAlchemyError: Raised when an error related to the database occurs during the 
        transaction, which results in rolling back the session.
        Exception: Catches general exceptions and logs an error.
    """
    if current_user.role == 1:
        # Get the session ID and exam element from the form data
        session_id = request.form.get('session_id')
        exam_element = request.form.get('exam_element')
        exam_name = get_exam_name(exam_element)

        # Check for missing input data 
        if not session_id or not exam_element or not exam_name:
            flash('Invalid exam request. Missing required information.', 'danger')
            return redirect(url_for(PAGE_SESSIONS))

        # Check if an exam session already exists for this session and user
        existing_exam = Exam.query.filter_by(user_id=current_user.id,
                                             session_id=session_id,
                                             element=exam_element).first()
        if existing_exam:
            # flash(f'You already have an exam in progress for session {session_id}.', 'warning')
            return redirect(url_for('main.take_exam', exam_id=existing_exam.id))

        # Get the Exam Registration for the user and session
        exam_registration = ExamRegistration.query.filter_by(
            user_id=current_user.id,
            session_id=session_id,
            valid=True
        ).first()

        if not exam_registration:
            flash('You are not registered for this exam session or your registration is invalid.',
                  'danger')
            return redirect(url_for(PAGE_SESSIONS))

        # Get Exam Session
        exam_session = ExamSession.query.get(session_id)

        # Check if the user is registered for the correct exam element
        if (exam_element == '2' and exam_registration.tech):
            pool_id = exam_session.tech_pool_id
        elif (exam_element == '3' and not exam_registration.gen):
            pool_id = exam_session.gen_pool_id
        elif (exam_element == '4' and not exam_registration.extra):
            pool_id = exam_session.extra_pool_id
        else:
            flash(f'You are not registered for the {exam_name} exam.', 'danger')
            return redirect(url_for(PAGE_SESSIONS))

        try:
            # Create a new exam session
            new_exam = Exam(
                user_id=current_user.id,
                pool_id=pool_id,
                session_id=session_id,
                element=exam_element,
                open=True
            )
            db.session.add(new_exam)
            db.session.commit()

            # Add the questions to the exam - TODO: Change this to the algorithm
            questions = Question.query.filter_by(pool_id=pool_id).limit(35).all()
            for question in questions:
                new_answer = ExamAnswer(
                    exam_id=new_exam.id,
                    question_id=question.id,
                    question_number=question.number,
                    correct_answer=question.correct_answer
                )
                db.session.add(new_answer)
            db.session.commit()

            return redirect(url_for('main.take_exam', exam_id=new_exam.id))

        except SQLAlchemyError as db_error:
            db.session.rollback()
            flash('A database error occurred while creating the exam session. Please try again.',
                  'danger')
            app.logger.error(f'Database error creating exam session: {str(db_error)}')
            return redirect(url_for(PAGE_SESSIONS))

        except Exception as e: # pylint: disable=W0718
            db.session.rollback()
            flash('An unexpected error occurred. Please try again later.', 'danger')
            app.logger.error(f'Error creating exam session: {str(e)}')
            return redirect(url_for(PAGE_SESSIONS))

    # If no HC account exists, redirect to the logout page
    flash(MSG_ACCESS_DENIED, "danger")
    return redirect(url_for(PAGE_LOGOUT))

@main.route('/exam/<int:exam_id>', methods=['POST'])
@login_required
def take_exam(exam_id):
    """
    Route to take an exam.
    """
    if current_user.role == 1:
         # Check if exam_id exists in the Exam table
        exam = Exam.query.get(exam_id)
        if not exam:
            flash('Invalid exam ID. Please try again.', 'danger')
            return redirect(url_for(PAGE_SESSIONS))

        # Use the exam.id property to load the answers from the ExamAnswer table
        exam_answers = ExamAnswer.query.filter_by(exam_id=exam.id).all()

        # Load the questions from the Questions table based on the question_id in ExamAnswers
        question_ids = [answer.question_id for answer in exam_answers]
        questions = Question.query.filter(Question.id.in_(question_ids)).all()

        return render_template('exam.html',
                               exam=exam,
                               exam_answers=exam_answers,
                               questions=questions)

    # If no HC account exists, redirect to the logout page
    flash(MSG_ACCESS_DENIED, "danger")
    return redirect(url_for(PAGE_LOGOUT))


##########################################
#                                        #
#     VE (Volunteer Examiner) Routes     #
#                                        #
##########################################

# VE Profile Route
@main.route('/ve/profile')
@login_required
def ve_profile():
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
    flash(MSG_ACCESS_DENIED, "danger")
    return redirect(url_for(PAGE_LOGOUT))

# Question Pools Route
@main.route('/ve/pools')
@login_required
def pools():
    """Render the pools page of the application.

    Returns:
        Response: The rendered 'pools.html' template.
    """
    # Check if the current user has role 2
    if current_user.role == 2:
        # If a VE account exists

        # Get all question pools from the database
        question_pools = load_question_pools()
        for question_pool in question_pools:
            question_count = Question.query.filter_by(pool_id=question_pool.id).count()
            question_pool.question_count = question_count
        return render_template('pools.html', question_pools=question_pools)

    # If no VE account exists, redirect to the logout page
    flash(MSG_ACCESS_DENIED, "danger")
    return redirect(url_for(PAGE_LOGOUT))

# Route to create question pools
@main.route('/ve/create_pool', methods=['POST'])
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
    # Check if the current user has role 2
    if current_user.role == 2:
        # If a VE account exists
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

    # If no VE account exists, redirect to the logout page
    flash(MSG_ACCESS_DENIED, "danger")
    return redirect(url_for(PAGE_LOGOUT))

# Route to upload question pools
@main.route('/ve/upload_questions/<int:pool_id>', methods=['POST'])
@login_required
def upload_questions(pool_id):
    """Handle the CSV upload for questions and associate them with the given pool_id."""
    # Check if the current user has role 2
    if current_user.role == 2:
        # If a VE account exists
        file = request.files.get('file')

        if not file:
            return jsonify({"error": "No file provided."}), 400

        filename = secure_filename(file.filename)
        if not filename.endswith('.csv'):
            return jsonify({"error": "Invalid file type. Only CSV files are allowed."}), 400

        # Parse the CSV file
        file_stream = TextIOWrapper(file.stream, encoding='utf-8')
        csv_reader = csv.DictReader(file_stream)

        tlis = {}
        questions = []
        for row in csv_reader:
            # Get the TLI and count questions
            tli = row['id'][:3]
            if tli in tlis:
                tlis[tli] += 1
            else:
                tlis[tli] = 1

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

        for tli, count in tlis.items():
            # Create a TLI count entry for each TLI code
            new_tli = TLI(pool_id=pool_id, tli=tli, quantity=count)
            db.session.add(new_tli)

        # Add all questions to the database
        db.session.bulk_save_objects(questions)
        db.session.commit()

        return jsonify({"success": True}), 200

    # If no VE account exists, redirect to the logout page
    flash(MSG_ACCESS_DENIED, "danger")
    return redirect(url_for(PAGE_LOGOUT))

# Route to delete question pools
@main.route('/ve/delete_pool/<int:pool_id>', methods=['DELETE'])
@login_required
def delete_pool(pool_id):
    """
    Deletes a question pool, all associated questions, and any diagrams linked to the pool.

    This route handles the deletion of an exam pool, ensuring that the pool's questions 
    and diagrams are removed from both the database and the server. Only users with 
    role 2 can perform this operation.

    Args:
        pool_id (int): The ID of the pool to be deleted.

    Returns:
        - 200 JSON response: {"success": True} on successful deletion.
        - 404 JSON response: {"error": "Pool not found."} if the pool ID is invalid.
        - 404 JSON response: {"error": "Diagram file not found."} if any associated diagram 
          file is missing from the server.
        - Redirect to the logout page if the user does not have the appropriate role.
    """
    if current_user.role == 2:
        # Find the pool by ID
        pool = db.session.get(Pool, pool_id)
        if not pool:
            return jsonify({"error": "Pool not found."}), 404

        # Delete all questions associated with the pool
        Question.query.filter_by(pool_id=pool_id).delete()
        TLI.query.filter_by(pool_id=pool_id).delete()

        # Delete all diagrams associated with the pool
        diagrams = ExamDiagram.query.filter_by(pool_id=pool_id).all()
        upload_folder = app.config['UPLOAD_FOLDER']

        for diagram in diagrams:
            # Delete the diagram file from the server
            file_path = os.path.join(upload_folder, os.path.basename(diagram.path))
            if os.path.exists(file_path):
                os.remove(file_path)
            else:
                app.logger.error(f"File does not exist: {file_path}")

            # Delete the diagram from the database
            db.session.delete(diagram)

        # Delete the pool itself
        db.session.delete(pool)
        db.session.commit()

        return jsonify({"success": True}), 200

    # If no VE account exists, redirect to the logout page
    flash(MSG_ACCESS_DENIED, "danger")
    return redirect(url_for(PAGE_LOGOUT))

# Route to show exam sessions page
@main.route('/ve/sessions')
@login_required
def ve_sessions():
    """Render the sessions page of the application.

    Returns:
        Response: The rendered 've_sessions.html' template.
    """
    if current_user.role == 2:
        # If a VE account exists
        # Get all test sessions from the database
        test_sessions = \
            ExamSession.query.order_by(ExamSession.session_date.desc()).all()
        question_pools=Pool.query.all()

        tech_pool_options={}
        general_pool_options={}
        extra_pool_options={}

        for pool in question_pools:
            if pool.element == 2:
                tech_pool_options[pool.id] = \
                    f"{pool.name} {pool.start_date.strftime('%Y')}-{pool.end_date.strftime('%Y')}"
            elif pool.element == 3:
                general_pool_options[pool.id] = \
                    f"{pool.name} {pool.start_date.strftime('%Y')}-{pool.end_date.strftime('%Y')}"
            elif pool.element == 4:
                extra_pool_options[pool.id] = \
                    f"{pool.name} {pool.start_date.strftime('%Y')}-{pool.end_date.strftime('%Y')}"

        current_date = datetime.now().date()
        return render_template('ve_sessions.html',
                            test_sessions=test_sessions,
                            tech_pool_options=tech_pool_options,
                            general_pool_options=general_pool_options,
                            extra_pool_options=extra_pool_options,
                            current_date=current_date)

    # If no VE account exists, redirect to the logout page
    flash(MSG_ACCESS_DENIED, "danger")
    return redirect(url_for(PAGE_LOGOUT))

# Route to create test sessions
@main.route('/ve/create_session', methods=['POST'])
@login_required
def create_session():
    """
    Creates a new test session and stores it in the database.

    This route handles the creation of a test session by accepting form data
    through a POST request. The form data should include the session date and three pool_id values,
    one for each exam element. If any of the required fields are missing, a 400 error 
    is returned with a message indicating that all fields are required.

    On successful creation of the test session, the session is added to the database
    and a JSON response with success status is returned.

    Returns:
        Response: A JSON response with a success message and a 200 status code on
        successful creation, or a 400 status code with an error message if any field
        is missing.
    """
    if current_user.role == 2:
        # Debugging for current user role
        print(f"Current user role: {current_user.role}")

        # Get the form data
        start_date = request.form.get('start_date')
        tech_pool_id = request.form.get('tech_pool')
        general_pool_id = request.form.get('general_pool')
        extra_pool_id = request.form.get('extra_pool')

        # Debugging the received form data
        print(f"Form Data Received - Start Date: {start_date}, Tech Pool ID: {tech_pool_id}, " + \
              "General Pool ID: {general_pool_id}, Extra Pool ID: {extra_pool_id}")

        # Validate the form data
        if not start_date or not tech_pool_id or not general_pool_id or not extra_pool_id:
            print("Form validation failed")
            return jsonify({"error": "All fields are required."}), 400

        # Convert the session_date to a Python datetime object
        session_date = datetime.strptime(start_date, '%Y-%m-%d').date()

        # Create a new session entry in the database
        new_session = ExamSession(
            session_date=session_date,
            tech_pool_id=tech_pool_id,
            gen_pool_id=general_pool_id,
            extra_pool_id=extra_pool_id,
        )

        # Debugging session creation
        print(f"Creating session: {new_session}")

        db.session.add(new_session)
        db.session.commit()

        print("Session successfully created and committed")
        return jsonify({"success": True}), 200

    # If no VE account exists, redirect to the logout page
    flash(MSG_ACCESS_DENIED, "danger")
    return redirect(url_for(PAGE_LOGOUT))

# Route to open a session
@main.route('/ve/open_session/<int:session_id>', methods=['POST'])
@login_required
def open_session(session_id):
    """
    Opens a test session by setting the current time as the start_time and updating the status.
    """
    if current_user.role == 2:
        # If a VE account exists
        session = db.session.get(ExamSession, session_id)

        # Check if the session exists
        if session is None:
            return jsonify({"error": "Session not found."}), 404

        # Set the start time to the current time and mark the session as open
        session.start_time = datetime.now()
        session.status = True
        db.session.commit()

        return jsonify({"success": True}), 200

    # If no VE account exists, redirect to the logout page
    flash(MSG_ACCESS_DENIED, "danger")
    return redirect(url_for(PAGE_LOGOUT))

# Route to close a session
@main.route('/ve/close_session/<int:session_id>', methods=['POST'])
@login_required
def close_session(session_id):
    """Closes a test session by setting the current time as the end_time and updating the status."""
    if current_user.role == 2:
        # Retrieve the session, and return a 404 error if not found
        session = db.session.get(ExamSession, session_id)
        if session is None:
            return jsonify({"error": "Session not found."}), 404

        # Set the end time to the current time and mark the session as closed
        session.end_time = datetime.now()
        session.status = False
        db.session.commit()

        return jsonify({"success": True}), 200

    # If no VE account exists, redirect to the logout page
    flash(MSG_ACCESS_DENIED, "danger")
    return redirect(url_for(PAGE_LOGOUT))

# Route to upload exam diagrams
@main.route('/ve/upload_diagram/<int:pool_id>', methods=['POST'])
@login_required
def upload_diagram(pool_id):
    """
    Uploads an exam diagram to the server and stores its metadata in the database.

    This route handles the process of uploading a diagram file associated with 
    a specific exam pool. It ensures that the uploaded file is valid, saves the 
    file securely, and stores the diagram's metadata (including the path) in the 
    database. 

    Args:
        pool_id (int): The ID of the exam pool to which the diagram belongs.

    Returns:
        - Redirects back to the pools page or the referrer upon success or failure.
    """
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.referrer or url_for('main.pools'))


    file = request.files['file']
    diagram_name = request.form.get('diagram_name')

    if file.filename == '':
        flash('No selected file')
        return redirect(request.referrer or url_for('main.pools'))

    if file and allowed_file(file.filename):
        # Secure the filename to prevent issues with directory traversal
        filename = secure_filename(f"{pool_id}_{file.filename}")

        # Construct the full path to save the file using current_app
        upload_folder = app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, filename)

        # Relative path to store in the database
        relative_path = f"diagrams/{filename}"

        # Debugging output to verify the path
        app.logger.info(f"File path to save: {file_path}")
        app.logger.info(f"Path to store in database: {relative_path}")

        # Ensure the directory exists
        if not os.path.exists(upload_folder):
            app.logger.error(f"Directory does not exist: {upload_folder}")
            flash('Upload directory does not exist.')
            return redirect(request.referrer or url_for('main.pools'))

        app.logger.info(f"Directory exists: {upload_folder}")

        try:
            # Save the file to the designated folder
            file.save(file_path)

            # Store the diagram information in the database
            new_diagram = ExamDiagram(
                pool_id=pool_id,
                name=diagram_name,
                path=relative_path  # Store the relative path, not the full path
            )
            db.session.add(new_diagram)
            db.session.commit()

            flash('Diagram uploaded successfully')
            return redirect(url_for('main.pools', pool_id=pool_id))

        except SQLAlchemyError as e:
            db.session.rollback()  # Rollback the session in case of an error
            app.logger.error(f"Error saving diagram to the database: {e}")
            flash('An error occurred while saving the diagram to the database.')

            return redirect(request.referrer or url_for('main.pools'))

    else:
        flash('Invalid file type. Allowed types: png, jpg, jpeg, gif')
        return redirect(request.referrer or url_for('main.pools'))

# Route to delete diagrams
@main.route('/ve/delete_diagram/<int:diagram_id>', methods=['DELETE'])
@login_required
def delete_diagram(diagram_id):
    """
    Deletes an exam diagram from both the server and the database.

    This route handles the deletion of a diagram associated with an exam pool. 
    It ensures that only users with the appropriate role (role 2) can perform 
    the deletion. The method checks for the existence of the diagram, removes 
    the file from the server, deletes the diagram record from the database, 
    and handles any errors that may occur during the process.

    Args:
        diagram_id (int): The ID of the diagram to be deleted.

    Returns:
        - 200 JSON response: {"success": True} on successful deletion.
        - 404 JSON response: {"error": "Diagram not found."} if the diagram ID is invalid.
        - 404 JSON response: {"error": "Diagram file not found."} if the file does not exist on 
          the server.
        - Redirect to the logout page if the user does not have the appropriate role.
    """
    # Check if the current user has role 2
    if current_user.role == 2:
        # If a VE account exists
        # Find the diagram by ID
        diagram = db.session.get(ExamDiagram, diagram_id)
        if not diagram:
            return jsonify({"error": "Diagram not found."}), 404

        # Delete the diagram file from the server
        upload_folder = app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, os.path.basename(diagram.path))
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            app.logger.error(f"File does not exist: {file_path}")
            return jsonify({"error": "Diagram file not found."}), 404

        # Delete the diagram itself
        db.session.delete(diagram)
        db.session.commit()

        return jsonify({"success": True}), 200

    # If no VE account exists, redirect to the logout page
    flash(MSG_ACCESS_DENIED, "danger")
    return redirect(url_for(PAGE_LOGOUT))
