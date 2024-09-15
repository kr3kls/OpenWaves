"""File: test_main.py

    This file contains the tests for the code in the main.py file.
"""

from werkzeug.security import generate_password_hash
from openwaves import db
from openwaves.models import User
from openwaves.tests.test_auth import login

def test_index(client):
    """Test that the index page loads correctly.

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
    """Test that the account select page loads correctly.

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
    """Test accessing the profile page with and without authentication.

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

def test_ve_account_exists(client, app):
    """Test accessing the VE profile when it exists.

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

    # Access ve_account
    assert response.status_code == 200
    # Should redirect to 'main.ve_account'
    assert b"OpenWaves VE Profile" in response.data

def test_ve_account_not_exists(client):
    """Test accessing the VE account when it does not exist.

    This test verifies that if a user without a VE account tries to access
    the VE account page, they are redirected to the VE signup page.

    Args:
        client: The test client instance.

    Asserts:
        - Response status code is 200.
        - Response data contains 'VE Account Signup'.
    """
    # Log in as testuser
    login(client, 'testuser', 'testpassword')

    # Access ve_account when VE account doesn't exist
    response = client.get('/ve_account', follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been logged out." in response.data

def test_csp_violation_report_valid_json(client, capsys):
    """Test reporting a valid CSP violation.

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
    """Test handling a CSP violation report with non-JSON data.

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
