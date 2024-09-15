"""File: models.py

    This module defines the User model for the application.
"""

from flask_login import UserMixin
from .imports import db

class User(UserMixin, db.Model):
    """Database model for users.

    Represents a user in the application, storing essential user information.

    Attributes:
        id (int): The primary key for the user.
        username (str): The unique username for the user (max 20 characters).
        first_name (str): The user's first name (max 30 characters).
        last_name (str): The user's last name (max 30 characters).
        email (str): The user's email address (max 120 characters).
        password (str): The hashed password for the user (max 60 characters).
        role (int): The role of the user (e.g., 1 for HAM Candidate, 2 for VE).
        active (bool): Whether the user is active in the system (default True).
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        """Return a string representation of the user.

        Returns:
            str: A string showing the username and email of the user.
        """
        return f"User('{self.username}', '{self.email}')"
