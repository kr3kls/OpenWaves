"""File: main_ve.py

    This file contains the main routes and view functions for the ve routes in the application.
"""

import os
import csv
from datetime import datetime
from io import TextIOWrapper
from flask import Blueprint, jsonify, redirect, render_template, request, flash, url_for, \
    current_app as app
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from .imports import db, Pool, Question, TLI, ExamSession, ExamDiagram, Exam, ExamAnswer, User, \
    load_question_pools, allowed_file, get_exam_name, get_exam_score

main_ve = Blueprint('main_ve', __name__)

PAGE_LOGOUT = 'auth.logout'
PAGE_POOLS = 'main_ve.pools'
PAGE_SESSIONS = 'main_ve.ve_sessions'
MSG_ACCESS_DENIED = 'Access denied.'

##########################################
#                                        #
#     VE (Volunteer Examiner) Routes     #
#                                        #
##########################################

# VE Profile Route
@main_ve.route('/ve/profile')
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
    if current_user.role != 2:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

    # If a VE account exists, redirect to the VE profile page
    return render_template('ve_profile.html', ve_user=current_user)

# Question Pools Route
@main_ve.route('/ve/pools')
@login_required
def pools():
    """Render the pools page of the application.

    Returns:
        Response: The rendered 'pools.html' template.
    """
    # Check if the current user has role 2
    if current_user.role != 2:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

    # Get all question pools from the database
    question_pools = load_question_pools()
    for question_pool in question_pools:
        question_count = Question.query.filter_by(pool_id=question_pool.id).count()
        question_pool.question_count = question_count
    return render_template('pools.html', question_pools=question_pools)

# Route to create question pools
@main_ve.route('/ve/create_pool', methods=['POST'])
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
    if current_user.role != 2:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

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

# Route to upload question pools
@main_ve.route('/ve/upload_questions/<int:pool_id>', methods=['POST'])
@login_required
def upload_questions(pool_id):
    """Handle the CSV upload for questions and associate them with the given pool_id."""
    # Check if the current user has role 2
    if current_user.role != 2:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

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

# Route to delete question pools
@main_ve.route('/ve/delete_pool/<int:pool_id>', methods=['DELETE'])
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
    if current_user.role != 2:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

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

# Route to show exam sessions page
@main_ve.route('/ve/sessions')
@login_required
def ve_sessions():
    """Render the sessions page of the application.

    Returns:
        Response: The rendered 've_sessions.html' template.
    """
    if current_user.role != 2:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

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

# Route to create test sessions
@main_ve.route('/ve/create_session', methods=['POST'])
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
    if current_user.role != 2:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

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

# Route to open a session
@main_ve.route('/ve/open_session/<int:session_id>', methods=['POST'])
@login_required
def open_session(session_id):
    """
    Opens a test session by setting the current time as the start_time and updating the status.
    """
    if current_user.role != 2:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

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

# Route to close a session
@main_ve.route('/ve/close_session/<int:session_id>', methods=['POST'])
@login_required
def close_session(session_id):
    """Closes a test session by setting the current time as the end_time and updating the status."""
    if current_user.role != 2:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

    # Retrieve the session, and return a 404 error if not found
    session = db.session.get(ExamSession, session_id)
    if session is None:
        return jsonify({"error": "Session not found."}), 404

    # Check for open exams
    open_exams = Exam.query.filter_by(session_id=session_id, open=True).all()
    if open_exams:
        return jsonify({"error": "There are still open exams in this session."}), 400

    # Set the end time to the current time and mark the session as closed
    session.end_time = datetime.now()
    session.status = False
    db.session.commit()

    return jsonify({"success": True}), 200

# Route to upload exam diagrams
@main_ve.route('/ve/upload_diagram/<int:pool_id>', methods=['POST'])
@login_required
def upload_diagram(pool_id): # pylint: disable=R0911
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
    # Check for VE role
    if current_user.role != 2:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for(PAGE_POOLS))

    file = request.files['file']
    diagram_name = request.form.get('diagram_name')

    if file.filename == '':
        flash('No selected file')
        return redirect(url_for(PAGE_POOLS))

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
            return redirect(url_for(PAGE_POOLS))

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
            return redirect(url_for(PAGE_POOLS, pool_id=pool_id))

        except SQLAlchemyError as e:
            db.session.rollback()  # Rollback the session in case of an error
            app.logger.error(f"Error saving diagram to the database: {e}")
            flash('An error occurred while saving the diagram to the database.')

            return redirect(url_for(PAGE_POOLS))

    else:
        flash('Invalid file type. Allowed types: png, jpg, jpeg, gif')
        return redirect(url_for(PAGE_POOLS))

# Route to delete diagrams
@main_ve.route('/ve/delete_diagram/<int:diagram_id>', methods=['DELETE'])
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
    if current_user.role != 2:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

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

@main_ve.route('/ve/exam/results', methods=['POST'])
@login_required
def ve_exam_results():
    """
    Route to review the a completed exam.
    """
    # Check if the current user has role 2
    if current_user.role != 2:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

    # Get the form data
    session_id = request.form.get('session_id')
    exam_element = request.form.get('exam_element')
    hc_id = request.form.get('hc_id')

    # Validate form data
    if not session_id or not exam_element or not hc_id:
        flash('Invalid exam request.', 'danger')
        return redirect(url_for(PAGE_SESSIONS))

    # Get the HC user
    hc_user = db.session.get(User, hc_id)
    if not hc_user:
        flash('Invalid HC ID.', 'danger')
        return redirect(url_for(PAGE_SESSIONS))

    # Get the exam and related answers
    exam = Exam.query.filter_by(user_id=hc_id,session_id=session_id,element=exam_element).first()
    if not exam:
        flash('Invalid exam ID.', 'danger')
        return redirect(url_for(PAGE_SESSIONS))

    # Make sure exam is complete
    if exam.open:
        flash('Exam is still in progress.', 'danger')
        return redirect(url_for(PAGE_SESSIONS))

    # Get the exam answers
    exam_answers = \
        ExamAnswer.query.filter_by(exam_id=exam.id).order_by(ExamAnswer.question_number).all()

    # Get the exam name
    exam_name = get_exam_name(f'{exam.element}')

    exam_score_string = get_exam_score(exam_answers, exam.element)

    # Get the associated questions for review
    question_ids = [answer.question_id for answer in exam_answers]
    questions = Question.query.filter(Question.id.in_(question_ids)).all()

    # Create a dictionary of questions by ID for easier lookup
    question_dict = {question.id: question for question in questions}

    return render_template(
        'results.html',
        exam=exam,
        exam_answers=exam_answers,
        questions=question_dict,
        exam_name=exam_name,
        exam_score_string=exam_score_string,
        hc=hc_user,
        ve=True
    )

@main_ve.route('/ve/force_close_session/<int:session_id>', methods=['POST'])
@login_required
def force_close_session(session_id):
    """Force closes a session regardless of open exams."""
    if current_user.role != 2:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

    # Retrieve the session, and return a 404 error if not found
    session = db.session.get(ExamSession, session_id)
    if session is None:
        return jsonify({"error": "Session not found."}), 404

    # Set the end time to the current time and mark the session as closed
    session.end_time = datetime.now()
    session.status = False
    db.session.commit()

    return jsonify({"success": True}), 200

@main_ve.route('/ve/session/results/<int:session_id>', methods=['GET'])
@login_required
def ve_session_results(session_id):
    """
    Route to load all exam results for a given session.
    """
    # Check if the current user has the necessary role
    if current_user.role != 2:
        flash("Access denied.", "danger")
        return redirect(url_for(PAGE_LOGOUT))

    # Retrieve the session
    session = db.session.get(ExamSession, session_id)
    if session is None:
        flash("Session not found.", "danger")
        return redirect(url_for(PAGE_SESSIONS))

    # Query all exams associated with the session
    exams = db.session.query(
        Exam.id.label('exam_id'),
        Exam.user_id,
        Exam.element,
        User.first_name,
        User.last_name
    ).join(User, User.id == Exam.user_id).filter(Exam.session_id == session_id).all()

    # Prepare the formatted results list to include scores and pass/fail status
    formatted_results = []
    for exam in exams:
        # Retrieve the exam answers for this exam to calculate the score
        answers = ExamAnswer.query.filter_by(exam_id=exam.exam_id).all()

        # Calculate the number of correct answers
        correct_count = sum(1 for answer in answers if answer.answer == answer.correct_answer)

        # Determine the pass/fail threshold based on the element
        if exam.element in [2, 3]:
            pass_threshold = 26
        elif exam.element == 4:
            pass_threshold = 37
        else:
            pass_threshold = 0  # Fallback in case of unexpected element

        # Determine pass/fail status
        passed = correct_count >= pass_threshold

        # Add the exam result data to the formatted list
        formatted_results.append({
            "last_name": exam.last_name,
            "first_name": exam.first_name,
            "element": exam.element,
            "correct": correct_count,
            "passed": passed,
            "session_id": session_id,
            "hc_id": exam.user_id
        })

    # Render the template with the formatted exam results
    return render_template(
        'session_results.html',
        exam_results=formatted_results,
        session=session
    )

@main_ve.route('/ve/delete_session/<int:session_id>', methods=['DELETE'])
@login_required
def delete_session(session_id):
    """
    Route to delete an exam session by session ID.
    """
    # Check if the current user has role 2
    if current_user.role != 2:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

    # Retrieve the session from the database
    session = db.session.get(ExamSession, session_id)
    if session is None:
        return jsonify({"error": "Session not found."}), 404

    # Check for exams
    exams = Exam.query.filter_by(session_id=session_id).all()
    if exams:
        return jsonify({"error": "There are exams in this session."}), 400

    # Delete the session from the database
    try:
        db.session.delete(session)
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e: # pylint: disable=W0718
        # Log the error and send a failure response
        db.session.rollback()
        print(f"Error deleting session: {e}")
        return jsonify({"error": "Failed to delete the session. Please try again later."}), 500
