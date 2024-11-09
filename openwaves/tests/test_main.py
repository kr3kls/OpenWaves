"""File: test_main.py

    This file contains the tests for the code in the main.py file.
"""

from datetime import datetime
from flask import url_for
from werkzeug.security import generate_password_hash
from openwaves import db
from openwaves.imports import User, Pool, Question
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

def test_pools_page_no_pools(client, ve_user):
    """Test ID: UT-103
    Functional test: Verify the pools page displays correctly when no pools are available.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - The response status code is 200.
        - The response contains a message indicating that no question pools are available.
    """
    login(client, ve_user.username, 'vepassword')
    response = client.get('/ve/pools')

    assert response.status_code == 200
    assert b'No question pools found.' in response.data

def test_pools_page_with_pools(client, app, ve_user):
    """Test ID: UT-104
    Functional test: Verify the pools page correctly displays all pools with question counts.

    Args:
        client: The test client instance.
        app: The Flask application instance.
        ve_user: The VE user fixture.

    Asserts:
        - The response status code is 200.
        - Each pool's question count is displayed correctly.
    """
    with app.app_context():
        # Create test question pools
        pool1 = Pool(name='Tech',
                     element='2',
                     start_date=datetime.strptime('2022-07-01', '%Y-%m-%d'),
                     end_date=datetime.strptime('2026-06-30', '%Y-%m-%d'))
        pool2 = Pool(name='General',
                     element='3',
                     start_date=datetime.strptime('2023-07-01', '%Y-%m-%d'),
                     end_date=datetime.strptime('2027-06-30', '%Y-%m-%d'))
        db.session.add_all([pool1, pool2])
        db.session.commit()

        # Add questions to pool1
        question1 = Question(pool_id=pool1.id,
                             number = 'T1A01',
                             correct_answer = '2',
                             question = 'Which of the following is part of the Basis and Purpose ' \
                                + 'of the Amateur Radio Service?',
                             option_a = 'Providing personal radio communications for as many ' \
                                + 'citizens as possible',
                             option_b = 'Providing communications for international non-profit ' \
                                + 'organizations',
                             option_c = 'Advancing skills in the technical and communication ' \
                                + 'phases of the radio art',
                             option_d = 'All these choices are correct',
                             refs = '[97.1]')
        question2 = Question(pool_id=pool1.id, \
                            number = 'T1B09',
                             correct_answer = '3',
                             question = 'Why should you not set your transmit frequency to be ' \
                                + 'exactly at the edge of an amateur band or sub-band?',
                             option_a = 'To allow for calibration error in the transmitter ' \
                                + 'frequency display',
                             option_b = 'So that modulation sidebands do not extend beyond the ' \
                                + 'band edge',
                             option_c = 'To allow for transmitter frequency drift',
                             option_d = 'All these choices are correct',
                             refs = '[97.101(a), 97.301(a-e)]')
        db.session.add_all([question1, question2])
        db.session.commit()

    login(client, ve_user.username, 'vepassword')
    response = client.get('/ve/pools')

    assert response.status_code == 200
    print(response.data)
    code1 = '<td>1</td>\n                    <td>Tech</td>\n                    <td>2</td>\n' \
            + '                    <td>2022-07-01</td>\n                    ' \
            + '<td>2026-06-30</td>\n                    <td>\n                        \n' \
            + '                            2 questions\n                        \n' \
            + '                    </td>\n                    <td>\n                        ' \
            + '<button class="button is-small is-danger delete-pool-button" data-name="Tech" ' \
            + 'data-id="1">Delete</button>\n                    </td>\n                ' \
            + '</tr>\n'
    assert code1.encode() in response.data
    code2 = '<td>2</td>\n                    <td>General</td>\n                    <td>3</td>\n' \
            + '                    <td>2023-07-01</td>\n                    <td>2027-06-30</td>\n' \
            + '                    <td>\n                        \n                            ' \
            + '<!-- Display upload button when there are no questions -->\n                      ' \
            + '      <button class="button is-small is-light-button-color" id="upload-button-2">' \
            + 'Upload Questions</button>\n'
    assert code2.encode() in response.data

def test_pools_page_role_not_allowed(client):
    """Test ID: UT-105
    Negative test: Ensure that users without the VE role cannot access the pools page.

    Args:
        client: The test client instance.

    Asserts:
        - The response status code is 302 (redirect).
        - The response redirects to the logout page.
        - An 'Access denied' message is flashed.
    """
    login(client, 'TESTUSER', 'testpassword')

    response = client.get(url_for('main_ve.pools'), follow_redirects=True)

    assert response.status_code == 200
    assert b'Access denied' in response.data

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

def test_delete_diagram_access_denied(client):
    """Test ID: UT-175
    Test diagram deletion access denied for non-VE users.

    This test ensures that if a non-VE user attempts to delete a diagram, they are denied access.

    Args:
        client: The test client instance.

    Asserts:
        - The user is redirected to the logout page with an access denied message.
    """
    # Log in as a regular user (role 1)
    login(client, 'TESTUSER', 'testpassword')

    # Attempt to delete a diagram as a non-VE user
    response = client.delete('/ve/delete_diagram/1', follow_redirects=True)

    # Assert access is denied
    assert response.status_code == 200
    assert b'Access denied.' in response.data
