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
