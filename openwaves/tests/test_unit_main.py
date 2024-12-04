"""File: test_main.py

    This file contains the unit tests for the code in the main.py file.
"""

from openwaves.tests.test_unit_auth import login

####################################
#                                  #
#     Account Navigation Tests     #
#                                  #
####################################

def test_index(client):
    """Test ID: UT-12
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
    """Test ID: UT-13
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

def test_csp_violation_report_valid_json(client, capsys):
    """Test ID: UT-14
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
    """Test ID: UT-15
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
    """Test ID: UT-16
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

def test_pools_page_access_not_logged_in(client):
    """Test ID: UT-17
    Negative test: Verifies that unauthenticated users cannot access the question pools page.

    Args:
        client: The test client instance.

    Asserts:
        - The response data contains "Please log in to access this page.".
    """
    response = client.get('/ve/pools', follow_redirects=True)
    assert b'Please log in to access this page.' in response.data

def test_create_pool_not_logged_in(client):
    """Test ID: UT-18
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

def test_delete_pool_not_logged_in(client):
    """Test ID: UT-19
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
