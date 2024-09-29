"""File: test_registration.py

    This file contains the tests for the registration code in the main.py file.
"""

from flask import url_for
from openwaves.tests.test_auth import login

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
