"""File: test_main.py

    This file contains the tests for the code in the main.py file.
"""
import io
from datetime import datetime
from werkzeug.security import generate_password_hash
from openwaves import db
from openwaves.models import User, Pool, Question, TLI, ExamSession
from openwaves.tests.test_auth import login

####################################
#                                  #
#     Account Navigation Tests     #
#                                  #
####################################

def test_index(client):
    """Test ID: UT-23
    Test that the index page loads correctly.

    Args:
        client: The test client instance.

    Asserts:
        - Response status code is 200.
        - Response data contains "Welcome to OpenWaves".
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome to OpenWaves" in response.data

def test_account_select(client):
    """Test ID: UT-24
    Test that the account select page loads correctly.

    Args:
        client: The test client instance.

    Asserts:
        - Response status code is 200.
        - Response data contains "Choose Your Role".
    """
    response = client.get('/account_select')
    assert response.status_code == 200
    assert b"Choose Your Role" in response.data

def test_profile_access(client):
    """Test ID: UT-25
    Test accessing the profile page with and without authentication.

    This test ensures that:
    - Accessing the profile page without logging in redirects to the login page.
    - After logging in, the profile page loads correctly.

    Args:
        client: The test client instance.

    Asserts:
        - When not logged in:
            - Response status code is 200.
            - Response data contains "OpenWaves Login".
        - When logged in:
            - Response status code is 200.
            - Response data contains "OpenWaves Profile".
    """
    # Access profile without logging in
    response = client.get('/profile', follow_redirects=True)
    assert response.status_code == 200
    assert b"OpenWaves Login" in response.data  # Should redirect to login page

    # Log in and access profile
    response = login(client, 'testuser', 'testpassword')
    assert response.status_code == 200
    response = client.get('/profile')
    assert response.status_code == 200
    assert b"OpenWaves Profile" in response.data

def test_ve_profile_exists(client, app):
    """Test ID: UT-26
    Test accessing the VE profile when it exists.

    This test creates a VE account for 'testuser' and verifies that accessing
    the VE account page loads correctly.

    Args:
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - Response status code is 200.
        - Response data contains 'OpenWaves VE Profile'.
    """
    # Create a VE account for testuser
    with app.app_context():
        ve_user = User(
            username='VE_TESTUSER',
            first_name='Test',
            last_name='User',
            email='testuser@example.com',  # Same email as current_user
            password=generate_password_hash('vepassword', method='pbkdf2:sha256'),
            role=2
        )
        db.session.add(ve_user)
        db.session.commit()

    # Log in as testuser
    response = login(client, 've_testuser', 'vepassword')

    # Access ve_profile
    assert response.status_code == 200
    # Should redirect to 'main.ve_profile'
    assert b"OpenWaves VE Profile" in response.data

def test_ve_profile_not_exists(client):
    """Test ID: UT-27
    Test accessing the VE account when logged in as role 1.

    This test verifies that if a role 1 user tries to access
    the VE account page, they are logged out.

    Args:
        client: The test client instance.

    Asserts:
        - Response status code is 200.
        - Response data contains 'VE Account Signup'.
    """
    # Log in as testuser
    login(client, 'testuser', 'testpassword')

    # Access ve_profile when VE account as role 1
    response = client.get('/ve/profile', follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been logged out." in response.data

def test_csp_violation_report_valid_json(client, capsys):
    """Test ID: UT-28
    Test reporting a valid CSP violation.

    This test sends a valid CSP violation report and checks that it is processed
    correctly.

    Args:
        client: The test client instance.
        capsys: Pytest fixture to capture stdout and stderr.

    Asserts:
        - Response status code is 204 (No Content).
        - The violation is printed to stdout.
    """
    violation_data = {
        "csp-report": {
            "document-uri": "http://example.com",
            "violated-directive": "script-src 'self'",
            "original-policy": "default-src 'none'; script-src 'self';",
            "blocked-uri": "http://evil.com/script.js"
        }
    }
    response = client.post('/csp-violation-report-endpoint', json=violation_data)
    assert response.status_code == 204

    # Capture the print output
    captured = capsys.readouterr()
    assert "CSP Violation:" in captured.out

###############################
#                             #
#     Question Pool Tests     #
#                             #
###############################

def test_pools_page_access(client, ve_user):
    """Test ID: UT-46
    Functional test: Verifies that a VE user can access the question pools page.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - The response status code is 200.
        - The response contains the text "Question Pools".
    """
    login(client, ve_user.username, 'vepassword')
    response = client.get('/ve/pools')
    assert response.status_code == 200
    assert b'Question Pools' in response.data

def test_pools_page_access_as_regular_user(client):
    """Test ID: UT-47
    Negative test: Ensures that a regular user cannot access the question pools page.

    Args:
        client: The test client instance.

    Asserts:
        - The response data contains "Access denied.".
    """
    login(client, 'TESTUSER', 'testpassword')
    response = client.get('/ve/pools', follow_redirects=True)
    assert b'Access denied.' in response.data

def test_pools_page_access_not_logged_in(client):
    """Test ID: UT-48
    Negative test: Verifies that unauthenticated users cannot access the question pools page.

    Args:
        client: The test client instance.

    Asserts:
        - The response data contains "Please log in to access this page.".
    """
    response = client.get('/ve/pools', follow_redirects=True)
    assert b'Please log in to access this page.' in response.data

def test_create_pool_success(client, ve_user):
    """Test ID: UT-49
    Functional test: Verifies that a VE user can successfully create a new question pool.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - The response status code is 200.
        - The response contains a JSON success message.
        - The newly created pool is present in the database with the correct element number.
    """
    login(client, ve_user.username, 'vepassword')
    response = client.post('/ve/create_pool', data={
        'pool_name': 'Test Pool',
        'exam_element': '2',
        'start_date': '2023-01-01',
        'end_date': '2026-12-31'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json()['success'] is True
    # Verify the pool was created in the database
    with client.application.app_context():
        pool = Pool.query.filter_by(name='Test Pool').first()
        assert pool is not None
        assert pool.element == 2

def test_create_pool_missing_fields(client, ve_user):
    """Test ID: UT-50
    Negative test: Verifies that creating a question pool with missing fields returns an error.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - The response status code is 400.
        - The response contains a JSON error message stating "All fields are required.".
    """
    login(client, ve_user.username, 'vepassword')
    response = client.post('/ve/create_pool', data={
        'pool_name': '',
        'exam_element': '',
        'start_date': '',
        'end_date': ''
    }, follow_redirects=True)
    assert response.status_code == 400
    assert response.is_json
    assert 'All fields are required.' in response.get_json()['error']

def test_create_pool_access_as_regular_user(client):
    """Test ID: UT-51
    Negative test: Ensures that a regular user cannot create a question pool.

    Args:
        client: The test client instance.

    Asserts:
        - The response data contains "Access denied.".
    """
    login(client, 'TESTUSER', 'testpassword')
    response = client.post('/ve/create_pool', data={
        'pool_name': 'Unauthorized Pool',
        'exam_element': '2',
        'start_date': '2023-01-01',
        'end_date': '2026-12-31'
    }, follow_redirects=True)
    assert b'Access denied.' in response.data

def test_create_pool_not_logged_in(client):
    """Test ID: UT-52
    Negative test: Verifies that unauthenticated users cannot create a question pool.

    Args:
        client: The test client instance.

    Asserts:
        - The response data contains "Please log in to access this page.".
    """
    response = client.post('/ve/create_pool', data={
        'pool_name': 'Unauthorized Pool',
        'exam_element': '2',
        'start_date': '2023-01-01',
        'end_date': '2026-12-31'
    }, follow_redirects=True)
    assert b'Please log in to access this page.' in response.data

def test_upload_questions_success(client, ve_user):
    """Test ID: UT-53
    Functional test: Verifies that a VE user can successfully upload questions to a pool.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - The response status code is 200.
        - The response contains a JSON success message.
        - Two questions were added to the database, and one TLI entry was created.
    """
    # First, create a pool to upload questions to
    login(client, ve_user.username, 'vepassword')
    client.post('/ve/create_pool', data={
        'pool_name': 'Upload Test Pool',
        'exam_element': '2',
        'start_date': '2023-01-01',
        'end_date': '2026-12-31'
    }, follow_redirects=True)

    with client.application.app_context():
        pool = Pool.query.filter_by(name='Upload Test Pool').first()
        pool_id = pool.id

    # Prepare a CSV file-like object to upload
    csv_content = """id,correct,question,a,b,c,d,refs
T1A01,A,What is 1+1?,2,3,4,5,Reference1
T1A02,B,What is 2+2?,1,4,3,5,Reference2
"""
    data = {
        'file': (io.BytesIO(csv_content.encode('utf-8')), 'questions.csv')
    }

    response = client.post(f'/ve/upload_questions/{pool_id}',
                           data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json()['success'] is True

    # Verify that questions were added to the database
    with client.application.app_context():
        question_count = Question.query.filter_by(pool_id=pool_id).count()
        assert question_count == 2
        tli_count = TLI.query.filter_by(pool_id=pool_id).count()
        assert tli_count == 1  # Both questions have TLI starting with 'T1'

def test_upload_questions_no_file(client, ve_user):
    """Test ID: UT-54
    Negative test: Verifies that uploading questions without a file returns an error.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - The response status code is 400.
        - The response contains a JSON error message stating "No file provided.".
    """
    login(client, ve_user.username, 'vepassword')
    # Assume there's a pool with ID 1
    response = client.post('/ve/upload_questions/1', data={}, content_type='multipart/form-data')
    assert response.status_code == 400
    assert response.is_json
    assert 'No file provided.' in response.get_json()['error']

def test_upload_questions_invalid_file_type(client, ve_user):
    """Test ID: UT-55
    Negative test: Ensures that uploading a non-CSV file type returns an error.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - The response status code is 400.
        - The response contains an error message stating that only CSV files are allowed.
    """
    login(client, ve_user.username, 'vepassword')

    # Create a pool first
    client.post('/ve/create_pool', data={
        'pool_name': 'Invalid File Type Pool',
        'exam_element': '2',
        'start_date': '2023-01-01',
        'end_date': '2026-12-31'
    }, follow_redirects=True)

    with client.application.app_context():
        pool = Pool.query.filter_by(name='Invalid File Type Pool').first()
        pool_id = pool.id

    # Prepare a non-CSV file-like object to upload
    non_csv_content = "Not a CSV content"
    data = {
        'file': (io.BytesIO(non_csv_content.encode('utf-8')), 'questions.txt')
    }

    response = client.post(f'/ve/upload_questions/{pool_id}',
                           data=data, content_type='multipart/form-data')

    # Check for the appropriate error response
    assert response.status_code == 400
    assert b'Invalid file type. Only CSV files are allowed.' in response.data

def test_upload_questions_access_as_regular_user(client):
    """Test ID: UT-56
    Negative test: Ensures that a regular user cannot upload questions to a pool.

    Args:
        client: The test client instance.

    Asserts:
        - The response status code is 302.
        - After following the redirect, the response data contains "Access denied".
    """
    login(client, 'TESTUSER', 'testpassword')
    response = client.post('/ve/upload_questions/1', data={}, content_type='multipart/form-data')
    assert response.status_code == 302  # Check for the redirect status
    # Follow the redirect and check the final destination
    follow_response = client.get(response.headers["Location"], follow_redirects=True)
    assert b'Access denied' in follow_response.data

def test_delete_pool_success(client, ve_user):
    """Test ID: UT-57
    Functional test: Verifies that a VE user can successfully delete a question pool.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - The response status code is 200, indicating successful pool deletion.
        - The response contains a JSON success message.
        - The pool is confirmed to have been deleted from the database.
    """
    login(client, ve_user.username, 'vepassword')
    # Create a pool to delete
    client.post('/ve/create_pool', data={
        'pool_name': 'Pool to Delete',
        'exam_element': '2',
        'start_date': '2023-01-01',
        'end_date': '2026-12-31'
    }, follow_redirects=True)
    with client.application.app_context():
        pool = Pool.query.filter_by(name='Pool to Delete').first()
        pool_id = pool.id

    response = client.delete(f'/ve/delete_pool/{pool_id}')
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json()['success'] is True
    # Verify the pool was deleted
    with client.application.app_context():
        pool = db.session.get(Pool, pool_id)
        assert pool is None

def test_delete_pool_not_found(client, ve_user):
    """Test ID: UT-58
    Negative test: Ensures that deleting a non-existent pool returns an error.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - The response status code is 404.
        - The response contains a JSON error message stating "Pool not found.".
    """
    login(client, ve_user.username, 'vepassword')
    response = client.delete('/ve/delete_pool/9999')
    assert response.status_code == 404
    assert response.is_json
    assert 'Pool not found.' in response.get_json()['error']

def test_delete_pool_access_as_regular_user(client):
    """Test ID: UT-59
    Negative test: Verifies that a regular user cannot delete a question pool.

    Args:
        client: The test client instance.

    Asserts:
        - The response status code is 302.
        - After following the redirect, the response data contains "Access denied.".
    """
    login(client, 'TESTUSER', 'testpassword')
    response = client.delete('/ve/delete_pool/1')
    assert response.status_code == 302  # Check for the redirect status
    # Follow the redirect and check the final destination
    follow_response = client.get(response.headers["Location"], follow_redirects=True)
    assert b'Access denied' in follow_response.data

def test_delete_pool_not_logged_in(client):
    """Test ID: UT-60
    Negative test: Ensures that an unauthenticated user cannot delete a pool.

    Args:
        client: The test client instance.

    Asserts:
        - The response contains a message asking the user to log in.
        - The response status code indicates a redirect, and the final destination contains 
            "Please log in to access this page.".
    """
    response = client.delete('/ve/delete_pool/1', follow_redirects=True)
    assert b'Please log in to access this page.' in response.data

##########################
#                        #
#     Sessions Tests     #
#                        #
##########################

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
    assert b'Test Sessions' in response.data

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

def test_csp_violation_report_non_json(client, capsys):
    """Test ID: UT-29
    Test handling a CSP violation report with non-JSON data.

    This test sends invalid (non-JSON) data to the CSP violation endpoint and
    checks that it is handled gracefully.

    Args:
        client: The test client instance.
        capsys: Pytest fixture to capture stdout and stderr.

    Asserts:
        - Response status code is 204 (No Content).
        - A message indicating non-JSON data is printed to stdout.
    """
    response = client.post('/csp-violation-report-endpoint', data='non-json data')
    assert response.status_code == 204

    # Capture the print output
    captured = capsys.readouterr()
    assert "Received non-JSON CSP violation report" in captured.out
