"""File: test_main.py

    This file contains the tests for the code in the main.py file.
"""
import io
from werkzeug.security import generate_password_hash
from openwaves import db
from openwaves.imports import User, Pool, Question, TLI
from openwaves.tests.test_auth import login, logout

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


def test_profile_access(client, app):
    """Test ID: UT-25
    Test accessing the profile page with and without authentication.

    This test ensures that:
    - Accessing the profile page without logging in redirects to the login page.
    - After logging in, the profile page loads correctly.

    Args:
        client: The test client instance.
        app: The Flask application instance.

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
    logout(client)

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
    assert response.status_code == 200
    response = client.get('/profile', follow_redirects=True)
    assert response.status_code == 200
    assert b"Access denied." in response.data


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
