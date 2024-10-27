"""File: utils.py

    Utility functions for user password management.
"""

from werkzeug.security import generate_password_hash
from openwaves.models import Pool, ExamDiagram
from . import db
from .config import Config

def update_user_password(user, new_password):
    """Update the user's password with a new hashed password.

    Args:
        user (User): The user object whose password is to be updated.
        new_password (str): The new plaintext password to set for the user.

    Returns:
        None
    """
    # Generate the new hashed password
    hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

    # Update the user's password
    user.password = hashed_password
    db.session.commit()

# Helper function to map exam element to its name
def get_exam_name(exam_element):
    """Map exam element number to exam name."""
    if exam_element is not None:
        exam_map = {'2': 'Tech', '3': 'General', '4': 'Extra'}
        return exam_map.get(exam_element, '')
    return ''

# Helper function to check if user is already registered for the exam element
def is_already_registered(existing_registration, exam_element):
    """Check if the user is already registered for the given exam element."""
    if exam_element is not None and existing_registration is not None:
        if exam_element == '2' and existing_registration.tech:
            return True
        if exam_element == '3' and existing_registration.gen:
            return True
        if exam_element == '4' and existing_registration.extra:
            return True
    return False

# Helper function to remove registration for a specific exam element
def remove_exam_registration(existing_registration, exam_element):
    """Remove the user's registration for the given exam element."""
    if exam_element is not None and existing_registration is not None:
        if exam_element == '2':
            existing_registration.tech = False
        elif exam_element == '3':
            existing_registration.gen = False
        elif exam_element == '4':
            existing_registration.extra = False

# Helper function to load question pools
def load_question_pools():
    """Load the question pools from the database."""
    pools = Pool.query.order_by(Pool.element.asc(), Pool.start_date.asc()).all()
    diagrams = ExamDiagram.query.all()
    for pool in pools:
        pool.diagrams = [diagram for diagram in diagrams if diagram.pool_id == pool.id]
    return pools

# Helper function to check if a file has an allowed extension
def allowed_file(filename):
    """Check if a given filename has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# Helper function to check if a question requires a diagram
def requires_diagram(question):
    """Check if a question requires a diagram."""
    diagrams = ExamDiagram.query.filter_by(pool_id=question.pool_id).all()
    for diagram in diagrams:
        if diagram.name in question.question:
            return diagram
    return None

# Helper function to get the exam score
def get_exam_score(exam_answers, element):
    """Calculate the exam score based on the given questions."""
    score = 0
    score_max = 35 if element in [2, 3] else 50 if element == 4 else None
    for answer in exam_answers:
        if answer.answer == answer.correct_answer:
            score += 1
    str_score = f'Score: {score}/{score_max}'
    if score_max == 35 and score >= 26:
        str_score += ' (Pass)'
    elif score_max == 50 and score >= 37:
        str_score += ' (Pass)'
    else:
        str_score += ' (Fail)'
    return str_score
