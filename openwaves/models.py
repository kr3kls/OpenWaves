"""File: models.py

    This module defines the User model for the application.
"""
from datetime import datetime
from dataclasses import dataclass
from flask_login import UserMixin
from . import db

FK_POOL_ID = 'pool.id'

@dataclass
class User(UserMixin, db.Model): # pylint: disable=R0902
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

    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(20), unique=True, nullable=False)
    first_name: str = db.Column(db.String(30), nullable=False)
    last_name: str = db.Column(db.String(30), nullable=False)
    email: str = db.Column(db.String(120), nullable=False)
    password: str = db.Column(db.String(60), nullable=False)
    role: int = db.Column(db.Integer, nullable=False)
    active: bool = db.Column(db.Boolean, default=True)

    def __repr__(self):
        """Return a string representation of the user.

        Returns:
            str: A string showing the username and email of the user.
        """
        return f"User('{self.username}', '{self.email}')"

@dataclass
class Pool(db.Model):
    """Database model for question pools.
    
    Represents a pool of questions for an exam.
    
    Attributes:
        id (int): The primary key for the pool.
        name (str): The name of the pool.
        element (int): The element number for the pool.
        start_date (datetime): The start date for the pool.
        end_date (datetime): The end date for the pool.
    """

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(100), nullable=False)
    element: int = db.Column(db.Integer, nullable=False)
    start_date: datetime = db.Column(db.DateTime, nullable=False)
    end_date: datetime = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        """Return a string representation of the pool.

        Returns:
            str: A string showing the name of the pool.
        """
        return f"Pool('{self.name}, start:{self.start_date}, end:{self.end_date}')"

@dataclass
class Question(db.Model): # pylint: disable=R0902
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

    id: int = db.Column(db.Integer, primary_key=True)
    pool_id: int = db.Column(db.Integer, db.ForeignKey(FK_POOL_ID), nullable=False)
    number: str = db.Column(db.String(5), nullable=False)
    correct_answer: int = db.Column(db.Integer, nullable=False)
    question: str = db.Column(db.Text, nullable=False)
    option_a: str = db.Column(db.Text, nullable=False)
    option_b: str = db.Column(db.Text, nullable=False)
    option_c: str = db.Column(db.Text, nullable=False)
    option_d: str = db.Column(db.Text, nullable=False)
    refs: str = db.Column(db.Text)

    def __repr__(self):
        """Return a string representation of the question.

        Returns:
            str: A string showing the question text.
        """
        return f"Question('{self.question}')"

@dataclass
class TLI(db.Model):
    """Database model for TLI counts.
    
    Represents the number of questions for each TLI code in a pool.

    Attributes:
        id (int): The primary key for the TLI count.
        pool_id (int): The pool ID for the TLI count.
        tli (str): The TLI code for the count.
        quantity (int): The quantity of questions for the TLI code.
    """
    id: int = db.Column(db.Integer, primary_key=True)
    pool_id: int = db.Column(db.Integer, db.ForeignKey(FK_POOL_ID), nullable=False)
    tli: str = db.Column(db.String(3), nullable=False)
    quantity: int = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Pool: {self.pool_id}, TLI: {self.tli}, Quantity: {self.quantity}"

@dataclass
class ExamSession(db.Model): # pylint: disable=R0902
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

    id: int = db.Column(db.Integer, primary_key=True)
    session_date: datetime = db.Column(db.DateTime, nullable=False)
    start_time: datetime = db.Column(db.DateTime, nullable=True)
    end_time: datetime = db.Column(db.DateTime, nullable=True)
    tech_pool_id: int = db.Column(db.Integer, db.ForeignKey(FK_POOL_ID), nullable=False)
    gen_pool_id: int = db.Column(db.Integer, db.ForeignKey(FK_POOL_ID), nullable=False)
    extra_pool_id: int = db.Column(db.Integer, db.ForeignKey(FK_POOL_ID), nullable=False)
    status: bool = db.Column(db.Boolean, default=False)

    def __repr__(self):
        """Return a string representation of the exam session.

        Returns:
            str: A string showing the start and end times of the exam session.
        """
        return f"ExamSession('{self.session_date}')"

@dataclass
class ExamRegistration(db.Model):
    """Database model for exam registrations.
    
    Represents a exam session registration for users taking exams.
    
    Attributes:
        id (int): The primary key for the exam session.
        session_id (int): The foreign key for the session's id in ExamSession.
        user_id (int): The foreign key for the user's id in User.
        tech (bool): True if the candidate registered for element 2.
        gen (bool): True if the candidate registered for element 3.
        extra (bool): True if the candidate registered for element 4.
        valid (bool): Whether the VEs have approved the registration.
    """

    id: int = db.Column(db.Integer, primary_key=True)
    session_id: int = db.Column(db.Integer, db.ForeignKey('exam_session.id'), nullable=False)
    user_id: int = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tech: bool = db.Column(db.Boolean, default=False)
    gen: bool = db.Column(db.Boolean, default=False)
    extra: bool = db.Column(db.Boolean, default=False)
    valid: bool = db.Column(db.Boolean, default=True)
    def __repr__(self):
        """Return a string representation of the registration.

        Returns:
            str: A string showing the registration info.
        """
        return f"ExamRegistration('{self.user_id}', '{self.session_id}')"

@dataclass
class ExamDiagram(db.Model):
    """Database model for exam diagrams.
    
    Represents a diagram for an exam question.
    
    Attributes:
        id (int): The primary key for the exam diagram.
        pool_id (int): The foreign key for the pool's id in Pool.
        name (str): The diagram name
        path (str): The path to the diagram file.
    """

    id: int = db.Column(db.Integer, primary_key=True)
    pool_id: int = db.Column(db.Integer, db.ForeignKey(FK_POOL_ID), nullable=False)
    name: str = db.Column(db.String(100), nullable=False)
    path: str = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        """Return a string representation of the diagram.

        Returns:
            str: A string showing the diagram path.
        """
        return f"ExamDiagram('{self.path}')"

@dataclass
class Exam(db.Model):
    """Database model for exams.
    
    Represents an exam that is part of a session, associated with a user and a question pool.

    Attributes:
        id (int): The primary key for the exam.
        user_id (int): The foreign key referencing the user's id in the User model.
        pool_id (int): The foreign key referencing the pool's id in the Pool model.
        session_id (int): The foreign key referencing the session's id in the ExamSession model.
        element (int): The element number for the exam.
        open (bool): Indicates whether the exam is open (default is True).
    """

    id: int = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pool_id: int = db.Column(db.Integer, db.ForeignKey(FK_POOL_ID), nullable=False)
    session_id: int = db.Column(db.Integer, db.ForeignKey('exam_session.id'), nullable=False)
    element: int = db.Column(db.Integer, nullable=False)
    open: bool = db.Column(db.Boolean, default=True)

    def __repr__(self):
        """Return a string representation of the exam.

        Returns:
            str: A string showing the Exam information.
        """
        return f"Exam('{self.id}', user_id: '{self.user_id}', pool: '{self.pool_id}', " \
            + f"session: '{self.session_id}')"

@dataclass
class ExamAnswer(db.Model):
    """Database model for exam answers.
    
    Represents an answer to an exam question.

    Attributes:
        id (int): The primary key for the exam answer.
        exam_id (int): The foreign key referencing the exam's id in the Exam model.
        question_id (int): The foreign key referencing the question's id in the Question model.
        question_number (int): The number of the question in the exam.
        correct_answer (int): The correct answer to the question.
        answer (int, optional): The answer provided by the user.
    """

    id: int = db.Column(db.Integer, primary_key=True)
    exam_id: int = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    question_id: int = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    question_number: int = db.Column(db.Integer(), nullable=False)
    correct_answer: int = db.Column(db.Integer(), nullable=False)
    answer: int = db.Column(db.Integer(), nullable=True)

    def __repr__(self):
        """Return a string representation of the answer.

        Returns:
            str: A string showing the answer to the question.
        """
        return f"ExamAnswer('{self.answer}')"
