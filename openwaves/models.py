"""File: models.py

    This module defines the User model for the application.
"""

from flask_login import UserMixin
from . import db

FK_POOL_ID = 'pool.id'

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

class Pool(db.Model): # pylint: disable=R0903
    """Database model for question pools.
    
    Represents a pool of questions for an exam.
    
    Attributes:
        id (int): The primary key for the pool.
        name (str): The name of the pool.
        element (int): The element number for the pool.
        start_date (datetime): The start date for the pool.
        end_date (datetime): The end date for the pool.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    element = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        """Return a string representation of the pool.

        Returns:
            str: A string showing the name of the pool.
        """
        return f"Pool('{self.name}, start:{self.start_date}, end:{self.end_date}')"

class Question(db.Model): # pylint: disable=R0903
    """Database model for questions.

    Represents a question on an exam, including the question text and answer choices.

    Attributes:
        id (str): The primary key for the question.
        number (str): The question number (e.g., E1A01).
        pool_id (int): The pool ID for the question.
        correct_answer (int): The correct answer choice (a, b, c, d).
        question (str): The text of the question.
        choice_a (str): The text for choice A.
        choice_b (str): The text for choice B.
        choice_c (str): The text for choice C.
        choice_d (str): The text for choice D.
        refs (str): References for the question.
    """

    id = db.Column(db.Integer, primary_key=True)
    pool_id = db.Column(db.Integer, db.ForeignKey(FK_POOL_ID), nullable=False)
    number = db.Column(db.String(5), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    question = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.Text, nullable=False)
    option_b = db.Column(db.Text, nullable=False)
    option_c = db.Column(db.Text, nullable=False)
    option_d = db.Column(db.Text, nullable=False)
    refs = db.Column(db.Text)

    def __repr__(self):
        """Return a string representation of the question.

        Returns:
            str: A string showing the question text.
        """
        return f"Question('{self.question}')"

class TLI(db.Model): # pylint: disable=R0903
    """Database model for TLI counts.
    
    Represents the number of questions for each TLI code in a pool.

    Attributes:
        id (int): The primary key for the TLI count.
        pool_id (int): The pool ID for the TLI count.
        tli (str): The TLI code for the count.
        quantity (int): The quantity of questions for the TLI code.
    """
    id = db.Column(db.Integer, primary_key=True)
    pool_id = db.Column(db.Integer, db.ForeignKey(FK_POOL_ID), nullable=False)
    tli = db.Column(db.String(3), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Pool: {self.pool_id}, TLI: {self.tli}, Quantity: {self.quantity}"

class ExamSession(db.Model): # pylint: disable=R0903
    """Database model for exam sessions.
    
    Represents a exam session for users taking exams.
    
    Attributes:
        id (int): The primary key for the exam session.
        session_date (datetime): The date of the exam session.
        start_time (datetime): The start time for the exam session.
        end_time (datetime): The end time for the exam session.
        tech_pool_id (int): The pool ID for the Technician exam.
        gen_pool_id (int): The pool ID for the General exam.
        extra_pool_id (int): The pool ID for the Extra exam.
        status (bool): Whether the exam session is active (default False).
    """

    id = db.Column(db.Integer, primary_key=True)
    session_date = db.Column(db.DateTime, nullable=False)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    tech_pool_id = db.Column(db.Integer, db.ForeignKey(FK_POOL_ID), nullable=False)
    gen_pool_id = db.Column(db.Integer, db.ForeignKey(FK_POOL_ID), nullable=False)
    extra_pool_id = db.Column(db.Integer, db.ForeignKey(FK_POOL_ID), nullable=False)
    status = db.Column(db.Boolean, default=False)

    def __repr__(self):
        """Return a string representation of the exam session.

        Returns:
            str: A string showing the start and end times of the exam session.
        """
        return f"ExamSession('{self.session_date}')"
