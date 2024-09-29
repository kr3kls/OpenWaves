"""File: utils.py

    Utility functions for user password management.
"""

from werkzeug.security import generate_password_hash
from . import db

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
