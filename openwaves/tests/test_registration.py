"""File: test_registration.py

    This file contains the tests for the registration code in the main.py file.
"""

from datetime import datetime
from flask import url_for
from openwaves.tests.test_auth import login
from openwaves.imports import db, User, ExamSession, Pool, ExamRegistration

def test_cancel_registration_missing_session_id(client):
    """Test ID: UT-101
    Negative test: Ensures that an invalid cancellation request is handled when the session ID is
    missing.

    Args:
        client: The test client instance.

    Asserts:
        - Response status code is 302 (redirection).
        - The response redirects to the sessions page.
        - The appropriate error message is flashed when session ID is missing.
    """
    login(client, 'TESTUSER', 'testpassword')

    response = client.post(
        url_for('main.cancel_registration'),
        data={'exam_element': '2'}  # Missing session_id
    )

    assert response.status_code == 302
    assert response.location.endswith(url_for('main.sessions'))  # PAGE_SESSIONS
    with client.session_transaction() as session:
        assert 'Invalid cancellation request. Missing required information.' \
            in session['_flashes'][0][1]

def test_cancel_registration_missing_exam_element(client):
    """Test ID: UT-102
    Negative test: Ensures that an invalid cancellation request is handled when the exam element is
    missing.

    Args:
        client: The test client instance.

    Asserts:
        - Response status code is 302 (redirection).
        - The response redirects to the sessions page.
        - The appropriate error message is flashed when the exam element is missing.
    """
    login(client, 'TESTUSER', 'testpassword')

    response = client.post(
        url_for('main.cancel_registration'),
        data={'session_id': '123'}  # Missing exam_element
    )

    assert response.status_code == 302
    assert response.location.endswith(url_for('main.sessions'))  # PAGE_SESSIONS
    with client.session_transaction() as session:
        assert 'Invalid cancellation request. Missing required information.' \
            in session['_flashes'][0][1]

def test_cancel_registration_invalid_exam_element(client):
    """Test ID: UT-103
    Negative test: Ensures that an invalid cancellation request is handled when the exam element is
    invalid.

    Args:
        client: The test client instance.

    Asserts:
        - Response status code is 302 (redirection).
        - The response redirects to the sessions page.
        - The appropriate error message is flashed when the exam element is invalid.
    """
    login(client, 'TESTUSER', 'testpassword')

    response = client.post(
        url_for('main.cancel_registration'),
        data={'session_id': '123', 'exam_element': 'invalid'}
    )

    assert response.status_code == 302
    assert response.location.endswith(url_for('main.sessions'))  # PAGE_SESSIONS
    with client.session_transaction() as session:
        assert 'Invalid cancellation request. Missing required information.' \
            in session['_flashes'][0][1]

def test_cancel_registration_role_not_allowed(client, ve_user):
    """Test ID: UT-109
    Negative test: Ensure that users with the VE role cannot access the cancel registration page.

    Args:
        client: The test client instance.

    Asserts:
        - The response status code is 302 (redirect).
        - The response redirects to the logout page.
        - An 'Access denied' message is flashed.
    """
    login(client, ve_user.username, 'vepassword')

    response = client.post(
        url_for('main.cancel_registration'),
        data={'session_id': '123', 'exam_element': '2'},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b'Access denied' in response.data

def test_cancel_registration_invalid_exam_session_id(client):
    """Test ID: UT-110
    Negative test: Ensures that an invalid cancellation request is handled when the session id is
    invalid.

    Args:
        client: The test client instance.

    Asserts:
        - Response status code is 302 (redirection).
        - The response redirects to the sessions page.
        - The appropriate error message is flashed when the session id is invalid.
    """
    login(client, 'TESTUSER', 'testpassword')

    response = client.post(
        url_for('main.cancel_registration'),
        data={'session_id': '123', 'exam_element': '2'}
    )

    assert response.status_code == 302
    assert response.location.endswith(url_for('main.sessions'))  # PAGE_SESSIONS
    with client.session_transaction() as session:
        assert 'Exam session not found.' \
            in session['_flashes'][0][1]

def test_register_route_success(client, app):
    """Test ID: UT-93
    Test successful registration for an exam session.

    This test ensures that a user with role 1 can successfully register for an exam element.

    Args:
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - The registration is created in the database.
        - The user receives a success message.
    """
    with app.app_context():
        # Log in as the test user (role 1)
        user = User.query.filter_by(username="TESTUSER").first()
        login(client, user.username, "testpassword")

        # Create an exam session
        pool = Pool(
            name="Test Pool",
            element=2,
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2026, 12, 31)
        )
        db.session.add(pool)
        db.session.commit()

        exam_session = ExamSession(
            session_date=datetime.now(),
            tech_pool_id=pool.id,
            gen_pool_id=pool.id,
            extra_pool_id=pool.id,
            status=True
        )
        db.session.add(exam_session)
        db.session.commit()

        # Submit a registration request
        response = client.post('/register', data={
            'session_id': exam_session.id,
            'exam_element': '2'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Successfully registered for the Tech exam.' in response.data

        # Verify registration in the database
        registration = ExamRegistration.query.filter_by(
            session_id=exam_session.id,
            user_id=user.id
        ).first()
        assert registration is not None
        assert registration.tech is True

def test_register_route_already_registered(client, app):
    """Test ID: UT-94
    Test registration when the user is already registered for the exam element.

    This test ensures that attempting to register again for the same exam element 
    results in an appropriate error message.

    Args:
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - The user receives an error message.
        - No duplicate registrations are created.
    """
    with app.app_context():
        # Log in as the test user (role 1)
        user = User.query.filter_by(username="TESTUSER").first()
        login(client, user.username, "testpassword")

        # Create an exam session and register the user
        pool = Pool(
            name="Test Pool",
            element=2,
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2026, 12, 31)
        )
        db.session.add(pool)
        db.session.commit()

        exam_session = ExamSession(
            session_date=datetime.now(),
            tech_pool_id=pool.id,
            gen_pool_id=pool.id,
            extra_pool_id=pool.id,
            status=True
        )
        db.session.add(exam_session)
        db.session.commit()

        # Initial registration
        registration = ExamRegistration(
            session_id=exam_session.id,
            user_id=user.id,
            tech=True
        )
        db.session.add(registration)
        db.session.commit()

        # Attempt to register again for the same exam element
        response = client.post('/register', data={
            'session_id': exam_session.id,
            'exam_element': '2'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'You are already registered for the Tech exam.' in response.data

def test_register_route_missing_data(client, app):
    """Test ID: UT-95
    Test registration with missing form data.

    This test ensures that attempting to register without providing required form data 
    results in an appropriate error message.

    Args:
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - The user receives an error message about missing information.
    """
    with app.app_context():
        # Log in as the test user (role 1)
        user = User.query.filter_by(username="TESTUSER").first()
        login(client, user.username, "testpassword")

        # Attempt to register without session_id
        response = client.post('/register', data={
            'exam_element': '2'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Invalid registration request. Missing required information.' in response.data

def test_cancel_registration_success(client, app):
    """Test ID: UT-96
    Test successful cancellation of an exam registration.

    This test ensures that a user with role 1 can successfully cancel their registration 
    for an exam element.

    Args:
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - The registration is updated in the database.
        - The user receives a success message.
    """
    with app.app_context():
        # Log in as the test user (role 1)
        user = User.query.filter_by(username="TESTUSER").first()
        login(client, user.username, "testpassword")

        # Create an exam session and register the user
        pool = Pool(
            name="Test Pool",
            element=2,
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2026, 12, 31)
        )
        db.session.add(pool)
        db.session.commit()

        exam_session = ExamSession(
            session_date=datetime.now(),
            tech_pool_id=pool.id,
            gen_pool_id=pool.id,
            extra_pool_id=pool.id,
            status=True
        )
        db.session.add(exam_session)
        db.session.commit()

        # Initial registration
        registration = ExamRegistration(
            session_id=exam_session.id,
            user_id=user.id,
            tech=True
        )
        db.session.add(registration)
        db.session.commit()

        # Submit a cancellation request
        response = client.post('/cancel_registration', data={
            'session_id': exam_session.id,
            'exam_element': '2'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Successfully canceled registration for the Tech exam.' in response.data

        # Verify registration in the database
        updated_registration = ExamRegistration.query.filter_by(
            session_id=exam_session.id,
            user_id=user.id
        ).first()
        assert updated_registration.tech is False

def test_cancel_registration_not_registered(client, app):
    """Test ID: UT-97
    Test cancellation when the user is not registered for the exam element.

    This test ensures that attempting to cancel a registration for an exam element 
    the user is not registered for results in an appropriate error message.

    Args:
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - The user receives an error message.
    """
    with app.app_context():
        # Log in as the test user (role 1)
        user = User.query.filter_by(username="TESTUSER").first()
        login(client, user.username, "testpassword")

        # Create an exam session
        pool = Pool(
            name="Test Pool",
            element=2,
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2026, 12, 31)
        )
        db.session.add(pool)
        db.session.commit()

        exam_session = ExamSession(
            session_date=datetime.now(),
            tech_pool_id=pool.id,
            gen_pool_id=pool.id,
            extra_pool_id=pool.id,
            status=True
        )
        db.session.add(exam_session)
        db.session.commit()

        # Attempt to cancel registration without being registered
        response = client.post('/cancel_registration', data={
            'session_id': exam_session.id,
            'exam_element': '2'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'You are not registered for the Tech exam.' in response.data

def test_register_route_invalid_role(client, app):
    """Test ID: UT-98
    Test registration with a user who does not have role 1.

    This test ensures that a user with a role other than 1 cannot register for an exam.

    Args:
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - The user is redirected with an access denied message.
    """
    with app.app_context():
        # Create and log in as a user with role 2 (VE)
        ve_user = User(
            username="VEUSER2",
            first_name="VE",
            last_name="User",
            email="veuser2@example.com",
            password="vepassword",
            role=2,
            active=True
        )
        db.session.add(ve_user)
        db.session.commit()

        login(client, ve_user.username, "vepassword")

        # Attempt to register
        response = client.post('/register', data={
            'session_id': '1',
            'exam_element': '2'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Please log in to access this page.' in response.data
