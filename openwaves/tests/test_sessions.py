"""File: test_sessions.py

    This file contains the tests for the sessions code in the main.py file.
"""

from datetime import datetime
from flask import url_for
from openwaves import db
from openwaves.imports import User, Pool, ExamSession
from openwaves.tests.test_auth import login

#############################
#                           #
#     VE Sessions Tests     #
#                           #
#############################

def test_sessions_page_access(client, ve_user):
    """Test ID: UT-61
    Functional test: Verifies that a VE user can access the sessions page.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - Response status code is 200.
        - Response data contains "Test Sessions".
    """
    login(client, ve_user.username, 'vepassword')
    response = client.get('/ve/sessions')
    assert response.status_code == 200
    assert b'Exam Sessions' in response.data

def test_sessions_page_access_as_regular_user(client):
    """Test ID: UT-62
    Negative test: Ensures that a regular user cannot access the sessions page.

    Args:
        client: The test client instance.

    Asserts:
        - The response data contains "Access denied".
    """
    login(client, 'TESTUSER', 'testpassword')
    response = client.get('/ve/sessions', follow_redirects=True)
    assert b'Access denied.' in response.data

def test_sessions_page_access_not_logged_in(client):
    """Test ID: UT-63
    Negative test: Ensures that unauthenticated users cannot access the sessions page.

    Args:
        client: The test client instance.

    Asserts:
        - The response data contains a message asking the user to log in.
        - The status code indicates a redirect to the login page.
    """
    response = client.get('/ve/sessions', follow_redirects=True)
    assert b'Please log in to access this page.' in response.data

def test_create_session_success(client, ve_user):
    """Test ID: UT-64
    Functional test: Confirms that a VE user can successfully create a new test session.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - The test pools are created successfully.
        - The response after creating the session is successful (status 200) and returns a 
            success message in JSON.
        - The session is correctly created in the database with the proper pools assigned.
    """
    login(client, ve_user.username, 'vepassword')

    # First, create pools to associate with the session
    client.post('/ve/create_pool', data={
        'pool_name': 'Tech Pool',
        'exam_element': '2',
        'start_date': '2023-01-01',
        'end_date': '2026-12-31'
    })
    client.post('/ve/create_pool', data={
        'pool_name': 'General Pool',
        'exam_element': '3',
        'start_date': '2023-01-01',
        'end_date': '2026-12-31'
    })
    client.post('/ve/create_pool', data={
        'pool_name': 'Extra Pool',
        'exam_element': '4',
        'start_date': '2023-01-01',
        'end_date': '2026-12-31'
    })

    # Retrieve the created pools
    with client.application.app_context():
        tech_pool = Pool.query.filter_by(name='Tech Pool').first()
        general_pool = Pool.query.filter_by(name='General Pool').first()
        extra_pool = Pool.query.filter_by(name='Extra Pool').first()

        # Ensure pools were created
        assert tech_pool is not None
        assert general_pool is not None
        assert extra_pool is not None

        # Create the test session
        response = client.post('/ve/create_session', data={
            'start_date': '2023-09-01',
            'tech_pool': tech_pool.id,
            'general_pool': general_pool.id,
            'extra_pool': extra_pool.id
        })

        # Assert that session creation was successful
        assert response.status_code == 200
        assert response.is_json
        assert response.get_json()['success'] is True

        # Use the full datetime (with time) to retrieve the session
        session_date = datetime.strptime('2023-09-01', '%Y-%m-%d')
        session = ExamSession.query.filter(ExamSession.session_date == session_date).first()

        assert session is not None  # Check if the session is actually created
        assert session.tech_pool_id == tech_pool.id
        assert session.gen_pool_id == general_pool.id
        assert session.extra_pool_id == extra_pool.id

def test_create_session_missing_fields(client, ve_user):
    """Test ID: UT-65
    Negative test: Verifies that creating a session with missing fields returns an error.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - Response status code is 400.
        - The JSON response contains the error message 'All fields are required.'.
    """
    login(client, ve_user.username, 'vepassword')
    response = client.post('/ve/create_session', data={
        'start_date': '',
        'tech_pool': '',
        'general_pool': '',
        'extra_pool': ''
    })
    assert response.status_code == 400
    assert response.is_json
    assert 'All fields are required.' in response.get_json()['error']

def test_create_session_access_as_regular_user(client):
    """Test ID: UT-66
    Negative test: Ensures that a regular user cannot create a test session.

    Args:
        client: The test client instance.

    Asserts:
        - The response status code is 302.
        - The user is redirected to the logout page.
    """
    login(client, 'TESTUSER', 'testpassword')  # Login as a regular user
    response = client.post('/ve/create_session', data={
        'start_date': '2023-09-01',
        'tech_pool': '1',
        'general_pool': '1',
        'extra_pool': '1'
    }, follow_redirects=False)  # Don't follow the redirect automatically

    # Assert that the user is redirected to the logout page
    assert response.status_code == 302
    assert '/auth/logout' in response.headers['Location']

def test_create_session_not_logged_in(client):
    """Test ID: UT-67
    Negative test: Ensures that unauthenticated users cannot create a test session.

    Args:
        client: The test client instance.

    Asserts:
        - The response data contains a message asking the user to log in.
        - The status code indicates a redirect to the login page.
    """
    response = client.post('/ve/create_session', data={
        'start_date': '2023-09-01',
        'tech_pool': '1',
        'general_pool': '1',
        'extra_pool': '1'
    }, follow_redirects=True)
    assert b'Please log in to access this page.' in response.data

def test_open_session_success(client, ve_user):
    """Test ID: UT-68
    Functional test: Verifies that a VE user can open a test session.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - The necessary question pools are created successfully.
        - The test session is created and can be opened.
        - Response status code is 200.
        - The session is marked as open, and the start time is set.
    """
    login(client, ve_user.username, 'vepassword')

    # First, create the necessary pools and session
    client.post('/ve/create_pool', data={
        'pool_name': 'Tech Pool',
        'exam_element': '2',
        'start_date': '2023-01-01',
        'end_date': '2026-12-31'
    })
    client.post('/ve/create_pool', data={
        'pool_name': 'General Pool',
        'exam_element': '3',
        'start_date': '2023-01-01',
        'end_date': '2026-12-31'
    })
    client.post('/ve/create_pool', data={
        'pool_name': 'Extra Pool',
        'exam_element': '4',
        'start_date': '2023-01-01',
        'end_date': '2026-12-31'
    })

    with client.application.app_context():
        tech_pool = Pool.query.filter_by(name='Tech Pool').first()
        general_pool = Pool.query.filter_by(name='General Pool').first()
        extra_pool = Pool.query.filter_by(name='Extra Pool').first()

    # Create the test session
    client.post('/ve/create_session', data={
        'start_date': '2023-09-01',
        'tech_pool': tech_pool.id,
        'general_pool': general_pool.id,
        'extra_pool': extra_pool.id
    })

    # Check all sessions after the creation attempt
    with client.application.app_context():

        # Ensure the session date includes the time component
        session = ExamSession.query.filter(ExamSession.session_date == \
                                           datetime(2023, 9, 1, 0, 0, 0)).first()
        print(f"Session created: {session}")
        assert session is not None, "The session was not created."

    # Continue to open the session...
    session_id = session.id
    response = client.post(f'/ve/open_session/{session_id}', follow_redirects=True)
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json()['success'] is True

    # Verify the session is marked as open
    with client.application.app_context():
        session = db.session.get(ExamSession, session_id)
        assert session.status is True
        assert session.start_time is not None

def test_open_session_not_found(client, ve_user):
    """Test ID: UT-69
    Negative test: Ensures that trying to open a non-existent session returns a 404 error.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - Response status code is 404.
        - The JSON response contains the error message 'Session not found.'.
    """
    login(client, ve_user.username, 'vepassword')
    response = client.post('/ve/open_session/9999')

    # Check that the status code is 404
    assert response.status_code == 404

    # Check that the response contains the correct JSON error message
    assert response.is_json
    json_data = response.get_json()
    assert json_data['error'] == "Session not found."

def test_close_session_success(client, ve_user):
    """Test ID: UT-70
    Functional test: Verifies that a VE user can successfully close a test session.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - The necessary question pools are created successfully.
        - The test session is created and can be opened and closed.
        - Response status code is 200, and the JSON response indicates success.
        - The session status is marked as closed, and the end time is set.
    """
    login(client, ve_user.username, 'vepassword')

    # First, create the necessary pools and session
    client.post('/ve/create_pool', data={
        'pool_name': 'Tech Pool',
        'exam_element': '2',
        'start_date': '2023-01-01',
        'end_date': '2026-12-31'
    })
    client.post('/ve/create_pool', data={
        'pool_name': 'General Pool',
        'exam_element': '3',
        'start_date': '2023-01-01',
        'end_date': '2026-12-31'
    })
    client.post('/ve/create_pool', data={
        'pool_name': 'Extra Pool',
        'exam_element': '4',
        'start_date': '2023-01-01',
        'end_date': '2026-12-31'
    })

    # Retrieve the created pools
    with client.application.app_context():
        tech_pool = Pool.query.filter_by(name='Tech Pool').first()
        general_pool = Pool.query.filter_by(name='General Pool').first()
        extra_pool = Pool.query.filter_by(name='Extra Pool').first()

    # Create the test session
    client.post('/ve/create_session', data={
        'start_date': '2023-09-01',
        'tech_pool': tech_pool.id,
        'general_pool': general_pool.id,
        'extra_pool': extra_pool.id
    })

    # Add extra logging to debug session creation
    with client.application.app_context():

        # Query the created session by date, ignoring the time component
        session = ExamSession.query.filter(db.func.date(ExamSession.session_date) == \
                                           '2023-09-01').first()

        # Assert the session was created
        assert session is not None, "The session was not created."

        # Proceed to open the session
        session_id = session.id
        response = client.post(f'/ve/open_session/{session_id}', follow_redirects=True)

        # Assert that the session was opened successfully
        assert response.status_code == 200

        # Now close the session
        response = client.post(f'/ve/close_session/{session_id}', follow_redirects=True)

        # Assert that the session was closed successfully
        assert response.status_code == 200
        assert response.is_json
        assert response.get_json()['success'] is True

        # Verify that the session is closed
        closed_session = db.session.get(ExamSession, session_id)
        assert closed_session.status is False, "The session is still open."
        assert closed_session.end_time is not None, "The session end_time was not set."

def test_close_session_not_found(client, ve_user):
    """Test ID: UT-71
    Negative test: Ensures that trying to close a non-existent session returns a 404 error.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - Response status code is 404.
        - The JSON response contains the error message 'Session not found.'.
    """
    login(client, ve_user.username, 'vepassword')
    response = client.post('/ve/close_session/9999')

    # Check that the status code is 404
    assert response.status_code == 404

    # Check that the response contains the correct JSON error message
    assert response.is_json
    json_data = response.get_json()
    assert json_data['error'] == "Session not found."

def test_open_session_access_as_regular_user(client):
    """Test ID: UT-72
    Negative test: Ensures that a regular user cannot open a test session.

    Args:
        client: The test client instance.

    Asserts:
        - Response contains 'Access denied.' message.
    """
    login(client, 'TESTUSER', 'testpassword')
    response = client.post('/ve/open_session/1', follow_redirects=True)
    assert b'Access denied.' in response.data

def test_close_session_access_as_regular_user(client):
    """Test ID: UT-73
    Negative test: Ensures that a regular user cannot close a test session.

    Args:
        client: The test client instance.

    Asserts:
        - Response contains 'Access denied.' message.
    """
    login(client, 'TESTUSER', 'testpassword')
    response = client.post('/ve/close_session/1', follow_redirects=True)
    assert b'Access denied.' in response.data

def test_open_session_not_logged_in(client):
    """Test ID: UT-74
    Negative test: Ensures that an unauthenticated user cannot open a test session.

    Args:
        client: The test client instance.

    Asserts:
        - Response contains 'Please log in to access this page.' message.
    """
    response = client.post('/ve/open_session/1', follow_redirects=True)
    assert b'Please log in to access this page.' in response.data

def test_close_session_not_logged_in(client):
    """Test ID: UT-74
    Negative test: Ensures that an unauthenticated user cannot open a test session.

    Args:
        client: The test client instance.

    Asserts:
        - Response contains 'Please log in to access this page.' message.
    """
    response = client.post('/ve/close_session/1', follow_redirects=True)
    assert b'Please log in to access this page.' in response.data

def test_ve_sessions_pool_categorization(client, ve_user):
    """Test ID: UT-164
    Test categorization of question pools by element in the VE sessions route.

    This test ensures that the question pools are properly categorized into tech, general,
    and extra pool options based on their element values.

    Args:
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - The response contains the correct pool options categorized by exam element.
    """
    login(client, ve_user.username, "vepassword")

    # Create question pools for Tech, General, and Extra
    tech_pool = Pool(
        name="Tech Pool",
        element=2,
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2026, 12, 31)
    )
    general_pool = Pool(
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
    db.session.add_all([tech_pool, general_pool, extra_pool])
    db.session.commit()

    # Access the VE sessions route
    response = client.get(url_for('main.ve_sessions'))

    # Assert that the response contains the correct pool options
    assert response.status_code == 200
    assert f"{tech_pool.name} 2023-2026" in response.data.decode('utf-8')
    assert f"{general_pool.name} 2023-2026" in response.data.decode('utf-8')
    assert f"{extra_pool.name} 2023-2026" in response.data.decode('utf-8')

#############################
#                           #
#     HC Sessions Tests     #
#                           #
#############################

def test_sessions_route_as_user(client, app):
    """Test ID: UT-91
    Test the sessions route for a logged-in user with role 1 (HAM Candidate).

    This test ensures that a user with role 1 can access the sessions page and 
    that the correct information is rendered.

    Args:
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - The response status code is 200.
        - The response contains the expected content.
    """
    with app.app_context():
        # Log in as the test user (role 1)
        user = User.query.filter_by(username="TESTUSER").first()
        response = login(client, user.username, "testpassword")

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

        # Access the sessions page
        response = client.get('/sessions')
        assert response.status_code == 200
        assert b'Exam Sessions' in response.data
        assert bytes(exam_session.session_date.strftime('%m/%d/%Y'), 'utf-8') in response.data

def test_sessions_route_as_ve(client, ve_user):
    """Test ID: UT-99
    Negative test: Verifies that a VE user cannot access the sessions page.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - Response status code is 200.
        - Response data contains "You have been logged out.".
    """
    login(client, ve_user.username, 'vepassword')
    response = client.get('/sessions', follow_redirects=True)
    assert response.status_code == 200
    print(response.data)
    assert b"You have been logged out." in response.data

def test_sessions_route_as_unauthorized_user(client):
    """Test ID: UT-92
    Test the sessions route for an unauthorized user (not logged in or wrong role).

    This test ensures that a user who is not logged in or does not have role 1 
    cannot access the sessions page and is redirected appropriately.

    Args:
        client: The test client instance.

    Asserts:
        - The response status code is a redirect (302).
        - The user is redirected to the login page.
    """
    # Attempt to access the sessions page without logging in
    response = client.get('/sessions', follow_redirects=True)

    assert response.status_code == 200
    print(response.data)
    assert b'Please log in to access this page.' in response.data
