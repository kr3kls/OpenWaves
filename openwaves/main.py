"""File: main.py

    This file contains the main routes and view functions for the user routes in the application.
"""

from collections import defaultdict
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, \
    current_app as app
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from .imports import db, Question, ExamSession, ExamRegistration, ExamAnswer, Exam, get_exam_name, \
    is_already_registered, remove_exam_registration, requires_diagram, get_exam_score, generate_exam

PAGE_LOGOUT = 'auth.logout'
PAGE_SESSIONS = 'main.sessions'
PAGE_POOLS = 'main.pools'
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
    if current_user.role != 1:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

    # If a HC account exists, render the profile page
    return render_template('profile.html')

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
    if current_user.role != 1:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

    # Get all test sessions from the database
    # Combine the query for exam sessions, registrations, and completed exams
    combined_query = (
        db.session.query(ExamSession, ExamRegistration, Exam)
        .outerjoin(ExamRegistration, (ExamRegistration.session_id == ExamSession.id) &
                                    (ExamRegistration.user_id == current_user.id))
        .outerjoin(Exam, (Exam.session_id == ExamSession.id) &
                        (Exam.user_id == current_user.id))
        .order_by(ExamSession.session_date.desc(), ExamSession.id.desc())
        .all()
    )

    # Use a dictionary to aggregate data by session ID
    session_dict = defaultdict(lambda: {
        'tech_registered': False,
        'gen_registered': False,
        'extra_registered': False,
        'tech_exam_completed': False,
        'gen_exam_completed': False,
        'extra_exam_completed': False
    })

    for session, registration, exam in combined_query:
        session_id = session.id

        # Initialize or update the session entry in the dictionary
        session_info = session_dict[session_id]
        session_info.update({
            'id': session.id,
            'session_date': session.session_date,
            'status': 'Registration' if session.session_date.date() > datetime.now().date() or
                    (session.session_date.date() == datetime.now().date() \
                     and session.start_time is None)
                    else 'Open' if session.status else 'Closed'
        })

        # Update registration status for each exam element
        if registration:
            session_info['tech_registered'] |= registration.tech
            session_info['gen_registered'] |= registration.gen
            session_info['extra_registered'] |= registration.extra

        # Close exams that ended before submission
        if exam:
            if session.end_time and exam.open:
                exam.open = False
                db.session.commit()

        # Update exam completion status for each element
        if exam and not exam.open:
            if exam.element == 2:
                session_info['tech_exam_completed'] |= True
            elif exam.element == 3:
                session_info['gen_exam_completed'] |= True
            elif exam.element == 4:
                session_info['extra_exam_completed'] |= True

    # Convert the dictionary to a list for use in the template
    sessions_with_registrations = list(session_dict.values())
    current_date = datetime.now().date()

    return render_template(
        'sessions.html',
        exam_sessions=sessions_with_registrations,
        current_date=current_date
    )

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
    if current_user.role != 1:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

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
            extra=(exam_element == '4')
        )
        db.session.add(new_registration)

    # Commit changes and confirm registration
    db.session.commit()
    flash(f'Successfully registered for the {exam_name} exam.', 'success')
    return redirect(url_for(PAGE_SESSIONS))

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
    if current_user.role != 1:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

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
    if current_user.role != 1:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

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
    exam_session = db.session.get(ExamSession, session_id)

    # Check if the user is registered for the correct exam element
    if (exam_element == '2' and exam_registration.tech):
        pool_id = exam_session.tech_pool_id
    elif (exam_element == '3' and exam_registration.gen):
        pool_id = exam_session.gen_pool_id
    elif (exam_element == '4' and exam_registration.extra):
        pool_id = exam_session.extra_pool_id
    else:
        flash(f'You are not registered for the {exam_name} exam.', 'danger')
        return redirect(url_for(PAGE_SESSIONS))

    try:
        # Get the questions for the exam
        questions = generate_exam(pool_id)

        if not questions:
            flash('No questions found for the exam. Please try again later.', 'danger')
            return redirect(url_for(PAGE_SESSIONS))

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

        # Enumerate the questions and create exam answers
        for q_index, question in enumerate(questions):
            new_answer = ExamAnswer(
                exam_id=new_exam.id,
                question_id=question.id,
                question_number=q_index + 1,
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

@main.route('/exam/<int:exam_id>', methods=['GET', 'POST'])
@login_required
def take_exam(exam_id):
    """
    Route to take an exam and navigate through questions.
    """
    if current_user.role != 1:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

    # Retrieve the exam
    exam = db.session.get(Exam, exam_id)
    if not exam or not exam.open:
        flash('Invalid exam ID. Please try again.', 'danger')
        return redirect(url_for(PAGE_SESSIONS))

    # Retrieve answers for the exam
    exam_answers = \
        ExamAnswer.query.filter_by(exam_id=exam.id).order_by(ExamAnswer.question_id).all()

    # Get current question index (or default to the first question)
    current_question_index = int(request.args.get('index', 0))

    if request.method == 'POST':
        # Save user answer
        answer_value = request.form.get('answer')
        question_number = int(request.form.get('question_number'))
        if answer_value is not None:
            answer = ExamAnswer.query.filter_by(exam_id=exam_id,
                                                question_number=question_number).first()
            answer.answer = int(answer_value)
            db.session.commit()

        # Determine navigation
        if 'next' in request.form:
            current_question_index += 1
        elif 'back' in request.form:
            current_question_index -= 1
        elif 'review' in request.form:
            return redirect(url_for('main.review_exam', exam_id=exam.id))

    # Get the current question based on the index
    if current_question_index < 0:
        current_question_index = 0
    elif current_question_index >= len(exam_answers):
        current_question_index = len(exam_answers) - 1

    current_answer = exam_answers[current_question_index]
    current_question = db.session.get(Question, current_answer.question_id)

    diagram = requires_diagram(current_question)

    return render_template(
        'exam.html',
        exam=exam,
        question=current_question,
        answer=current_answer,
        current_index=current_question_index,
        total_questions=len(exam_answers),
        diagram=diagram
    )

@main.route('/exam/<int:exam_id>/review', methods=['GET'])
@login_required
def review_exam(exam_id):
    """
    Route to review the completed exam.
    """
    # Ensure the user has permission to review the exam
    if current_user.role != 1:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

    # Get the exam and related answers
    exam = db.session.get(Exam, exam_id)
    if not exam or not exam.open:
        flash('Invalid or closed exam ID.', 'danger')
        return redirect(url_for(PAGE_SESSIONS))

    if exam.user_id != current_user.id:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

    # Get the exam name
    exam_name = get_exam_name(f'{exam.element}')

    # Retrieve all answers related to the exam
    exam_answers = \
        ExamAnswer.query.filter_by(exam_id=exam.id).order_by(ExamAnswer.question_number).all()

    # Get the associated questions for review
    question_ids = [answer.question_id for answer in exam_answers]
    questions = Question.query.filter(Question.id.in_(question_ids)).all()

    # Create a dictionary of questions by ID for easier lookup
    question_dict = {question.id: question for question in questions}

    return render_template(
        'review.html',
        exam=exam,
        exam_answers=exam_answers,
        questions=question_dict,
        exam_name=exam_name
    )

@main.route('/exam/<int:exam_id>/finish', methods=['GET'])
@login_required
def finish_exam(exam_id):
    """
    Route to review the completed exam.
    """
    # Ensure the user has permission to review the exam
    if current_user.role != 1:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

    # Get the exam and related answers
    exam = db.session.get(Exam, exam_id)
    if not exam or not exam.open:
        flash('Invalid or closed exam ID.', 'danger')
        return redirect(url_for(PAGE_SESSIONS))

    if exam.user_id != current_user.id:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

    exam.open = False
    db.session.commit()

    return redirect(url_for('main.exam_results',
                            session_id=exam.session_id,
                            exam_element=exam.element))

@main.route('/exam/results', methods=['GET', 'POST'])
@login_required
def exam_results():
    """
    Route to review the completed exam.
    """
    # Handle both GET and POST methods
    if request.method == 'POST':
        session_id = request.form.get('session_id')
        exam_element = request.form.get('exam_element')
    else:
        session_id = request.args.get('session_id')
        exam_element = request.args.get('exam_element')

    # Validate session ID and exam element
    if not session_id or not exam_element:
        flash('Invalid exam request.', 'danger')
        return redirect(url_for(PAGE_SESSIONS))

    # Get the exam and related answers
    exam = Exam.query.filter_by(session_id=session_id,element=exam_element).first()
    if not exam:
        flash('Invalid exam ID.', 'danger')
        return redirect(url_for(PAGE_SESSIONS))

    # Close exams that were not finished
    exam_session = db.session.get(ExamSession, exam.session_id)
    if exam.open and exam_session.session_date.date() < datetime.now().date():
        exam.open = False
        db.session.commit()

    # Make sure exam is complete
    if exam.open:
        flash('Exam is still in progress.', 'danger')
        return redirect(url_for(PAGE_SESSIONS))

    # Ensure the user has permission to review the exam
    # Any role 2 is ok, but only the role 1 user who took the exam can review it
    if current_user.role == 1 and current_user.id != exam.user_id:
        flash(MSG_ACCESS_DENIED, "danger")
        return redirect(url_for(PAGE_LOGOUT))

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
        exam_score_string=exam_score_string
    )
