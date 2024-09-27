"""File: test_models.py

    This file contains the tests for the code in the models.py file.
"""

from datetime import datetime
from openwaves import db
from openwaves.models import User, Pool, Question, TLI, ExamSession, ExamRegistration

def test_user_creation(app):
    """Test ID: UT-76
    Test that a User can be created and saved to the database.

    This test ensures that a new user instance is properly created, added to the 
    database, and can be retrieved with the correct data.

    Args:
        app: The Flask application instance.

    Asserts:
        - The user ID is generated after saving to the database.
        - The user can be retrieved by username and matches the created user.
    """
    with app.app_context():
        user = User(
            username="testuser",
            first_name="Test",
            last_name="User",
            email="testuser@example.com",
            password="hashed_password",
            role=1,
            active=True
        )
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        retrieved_user = User.query.filter_by(username="testuser").first()
        assert retrieved_user == user


def test_user_repr(app):
    """Test ID: UT-77
    Test the __repr__ method of the User model.

    This test ensures that the string representation of the User object 
    correctly displays the username and email.

    Args:
        app: The Flask application instance.

    Asserts:
        - The __repr__ method returns the expected string format.
    """
    with app.app_context():
        user = User(
            username="testuser2",
            first_name="Test2",
            last_name="User2",
            email="testuser2@example.com",
            password="hashed_password",
            role=1,
            active=True
        )
        expected_repr = f"User('{user.username}', '{user.email}')"
        assert repr(user) == expected_repr


def test_pool_creation(app):
    """Test ID: UT-78
    Test that a Pool can be created and saved to the database.

    This test ensures that a new question pool instance is properly created, 
    added to the database, and can be retrieved by its name.

    Args:
        app: The Flask application instance.

    Asserts:
        - The pool ID is generated after saving to the database.
        - The pool can be retrieved by name and matches the created pool.
    """
    with app.app_context():
        pool = Pool(
            name="General Class Pool",
            element=3,
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2026, 12, 31)
        )
        db.session.add(pool)
        db.session.commit()

        assert pool.id is not None
        retrieved_pool = Pool.query.filter_by(name="General Class Pool").first()
        assert retrieved_pool == pool


def test_pool_repr(app):
    """Test ID: UT-79
    Test the __repr__ method of the Pool model.

    This test ensures that the string representation of the Pool object 
    correctly displays the pool name and date range.

    Args:
        app: The Flask application instance.

    Asserts:
        - The __repr__ method returns the expected string format showing the pool's name,
          start date, and end date.
    """
    with app.app_context():
        pool = Pool(
            name="Extra Class Pool",
            element=4,
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2026, 12, 31)
        )
        expected_repr = f"Pool('{pool.name}, start:{pool.start_date}, end:{pool.end_date}')"
        assert repr(pool) == expected_repr



def test_question_creation(app):
    """Test ID: UT-80
    Test that a Question can be created and saved to the database.

    This test ensures that a new question instance is properly created, 
    associated with a pool, added to the database, and can be retrieved 
    by its number.

    Args:
        app: The Flask application instance.

    Asserts:
        - The question ID is generated after saving to the database.
        - The question can be retrieved by its number and matches the created question.
    """
    with app.app_context():
        # Create a Pool to associate with the Question
        pool = Pool(
            name="Technician Class Pool",
            element=2,
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2026, 12, 31)
        )
        db.session.add(pool)
        db.session.commit()

        question = Question(
            pool_id=pool.id,
            number="T1A01",
            correct_answer="A",
            question="What is 1 + 1?",
            option_a="2",
            option_b="3",
            option_c="4",
            option_d="5",
            refs="Reference1"
        )
        db.session.add(question)
        db.session.commit()

        assert question.id is not None
        retrieved_question = Question.query.filter_by(number="T1A01").first()
        assert retrieved_question == question


def test_question_repr(app):
    """Test ID: UT-81
    Test the __repr__ method of the Question model.

    This test ensures that the string representation of the Question object 
    correctly displays the question text.

    Args:
        app: The Flask application instance.

    Asserts:
        - The __repr__ method returns the expected string format showing the question text.
    """
    with app.app_context():
        question = Question(
            pool_id=1,
            number="T1A02",
            correct_answer="B",
            question="What is 2 + 2?",
            option_a="3",
            option_b="4",
            option_c="5",
            option_d="6",
            refs="Reference2"
        )
        expected_repr = f"Question('{question.question}')"
        assert repr(question) == expected_repr


def test_tli_creation(app):
    """Test ID: UT-82
    Test that a TLI can be created and saved to the database.

    This test ensures that a new TLI instance is properly created, 
    associated with a pool, added to the database, and can be retrieved 
    by its TLI code.

    Args:
        app: The Flask application instance.

    Asserts:
        - The TLI ID is generated after saving to the database.
        - The TLI can be retrieved by its code and matches the created TLI.
    """
    with app.app_context():
        # Create a Pool to associate with the TLI
        pool = Pool(
            name="TLI Pool",
            element=2,
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2026, 12, 31)
        )
        db.session.add(pool)
        db.session.commit()

        tli = TLI(
            pool_id=pool.id,
            tli="T1",
            quantity=10
        )
        db.session.add(tli)
        db.session.commit()

        assert tli.id is not None
        retrieved_tli = TLI.query.filter_by(tli="T1").first()
        assert retrieved_tli == tli


def test_tli_repr(app):
    """Test ID: UT-83
    Test the __repr__ method of the TLI model.

    This test ensures that the string representation of the TLI object 
    correctly displays the pool ID, TLI code, and quantity of questions.

    Args:
        app: The Flask application instance.

    Asserts:
        - The __repr__ method returns the expected string format showing the pool ID, TLI, and
          quantity.
    """
    with app.app_context():
        tli = TLI(
            pool_id=1,
            tli="T2",
            quantity=5
        )
        expected_repr = f"Pool: {tli.pool_id}, TLI: {tli.tli}, Quantity: {tli.quantity}"
        assert repr(tli) == expected_repr


def test_exam_session_creation(app):
    """Test ID: UT-84
    Test that an ExamSession can be created and saved to the database.

    This test ensures that a new exam session instance is properly created, 
    associated with pools for each exam element, added to the database, and 
    can be retrieved by its session date.

    Args:
        app: The Flask application instance.

    Asserts:
        - The exam session ID is generated after saving to the database.
        - The exam session can be retrieved by its session date and matches the created session.
    """
    with app.app_context():
        # Create Pools for the ExamSession
        tech_pool = Pool(
            name="Tech Pool",
            element=2,
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2026, 12, 31)
        )
        gen_pool = Pool(
            name="General Pool",
            element=3,
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2026, 12, 31)
        )
        extra_pool = Pool(
            name="Extra Pool",
            element=4,
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2026, 12, 31)
        )
        db.session.add_all([tech_pool, gen_pool, extra_pool])
        db.session.commit()

        exam_session = ExamSession(
            session_date=datetime(2023, 9, 1),
            tech_pool_id=tech_pool.id,
            gen_pool_id=gen_pool.id,
            extra_pool_id=extra_pool.id,
            status=False
        )
        db.session.add(exam_session)
        db.session.commit()

        assert exam_session.id is not None
        retrieved_session = ExamSession.query.filter_by(session_date=datetime(2023, 9, 1)).first()
        assert retrieved_session == exam_session


def test_exam_session_repr(app):
    """Test ID: UT-85
    Test the __repr__ method of the ExamSession model.

    This test ensures that the string representation of the ExamSession object 
    correctly displays the session date.

    Args:
        app: The Flask application instance.

    Asserts:
        - The __repr__ method returns the expected string format showing the session date.
    """
    with app.app_context():
        exam_session = ExamSession(
            session_date=datetime(2023, 10, 1),
            tech_pool_id=1,
            gen_pool_id=1,
            extra_pool_id=1,
            status=True
        )
        expected_repr = f"ExamSession('{exam_session.session_date}')"
        assert repr(exam_session) == expected_repr


def test_exam_registration_creation(app):
    """Test ID: UT-86
    Test that an ExamRegistration can be created and saved to the database.

    This test ensures that a new exam registration instance is properly created, 
    associated with a user and exam session, added to the database, and can be 
    retrieved by the user ID.

    Args:
        app: The Flask application instance.

    Asserts:
        - The exam registration ID is generated after saving to the database.
        - The exam registration can be retrieved by its user ID and matches the created
          registration.
    """
    with app.app_context():
        # Create a User
        user = User(
            username="testcandidate",
            first_name="Test",
            last_name="Candidate",
            email="candidate@example.com",
            password="hashed_password",
            role=1,
            active=True
        )
        db.session.add(user)
        # Create an ExamSession
        exam_session = ExamSession(
            session_date=datetime(2023, 11, 1),
            tech_pool_id=1,
            gen_pool_id=1,
            extra_pool_id=1,
            status=False
        )
        db.session.add(exam_session)
        db.session.commit()

        registration = ExamRegistration(
            session_id=exam_session.id,
            user_id=user.id,
            tech=True,
            gen=False,
            extra=False,
            valid=False
        )
        db.session.add(registration)
        db.session.commit()

        assert registration.id is not None
        retrieved_registration = ExamRegistration.query.filter_by(user_id=user.id).first()
        assert retrieved_registration == registration


def test_exam_registration_repr(app):
    """Test ID: UT-87
    Test the __repr__ method of the ExamRegistration model.

    This test ensures that the string representation of the ExamRegistration object 
    correctly displays the user ID and session ID.

    Args:
        app: The Flask application instance.

    Asserts:
        - The __repr__ method returns the expected string format showing the user ID and session ID.
    """
    with app.app_context():
        registration = ExamRegistration(
            session_id=1,
            user_id=1,
            tech=False,
            gen=True,
            extra=False,
            valid=False
        )
        expected_repr = f"ExamRegistration('{registration.user_id}', '{registration.session_id}')"
        assert repr(registration) == expected_repr
