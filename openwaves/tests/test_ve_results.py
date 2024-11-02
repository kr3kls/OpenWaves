"""File: test_ve_results.py

    This file contains the tests for the ve exam results code in the main_ve.py file.
"""

import pytest
from flask import url_for
from openwaves.imports import db
from openwaves.tests.test_auth import login
from openwaves.tests.test_review_exam import setup_mock_exam

@pytest.mark.usefixtures("app")
def test_ve_exam_results_valid_request(client, ve_user):
    """Test ID: UT-244
    Test the ve_exam_results route with a valid POST request by an authorized VE user.

    Asserts:
        - The response status code is 200.
        - The exam review page displays the correct exam details and answers.
    """
    # Set up a mock exam with related data
    pool, exam_session, exam, question, exam_answer = setup_mock_exam(ve_user)  # pylint: disable=W0612

    # Log in as VE user
    response = login(client, ve_user.username, 'vepassword')
    assert response.status_code == 200

    # Simulate a POST request to view exam results
    response = client.post(
        url_for('main_ve.ve_exam_results'),
        data={'session_id': exam.session_id, 'exam_element': exam.element, 'hc_id': ve_user.id},
        follow_redirects=True
    )

    # Validate response contains exam results
    assert response.status_code == 200
    assert b'What is question 1?' in response.data
    assert b'Score: 1/35' in response.data  # Adjust based on scoring logic

@pytest.mark.usefixtures("app")
def test_ve_exam_results_unauthorized_role(client, user_to_toggle):
    """Test ID: UT-245
    Test the ve_exam_results route with an unauthorized user role.

    Asserts:
        - The response redirects to the logout page with an access denied message.
    """
    # Log in as a non-VE user
    response = login(client, user_to_toggle.username, 'password')
    assert response.status_code == 200

    # Attempt to access the exam results with unauthorized role
    response = client.post(
        url_for('main_ve.ve_exam_results'),
        data={'session_id': 1, 'exam_element': 2, 'hc_id': user_to_toggle.id},
        follow_redirects=True
    )

    # Validate redirection to the logout page with access denied message
    assert response.status_code == 200
    assert b'Access denied.' in response.data

@pytest.mark.usefixtures("app")
def test_ve_exam_results_invalid_form_data(client, ve_user):
    """Test ID: UT-246
    Test the ve_exam_results route with missing or invalid form data.

    Asserts:
        - The response redirects to the sessions page with an error message.
    """
    # Log in as VE user
    response = login(client, ve_user.username, 'vepassword')
    assert response.status_code == 200

    # Attempt to access results with missing form data
    response = client.post(
        url_for('main_ve.ve_exam_results'),
        data={'session_id': '', 'exam_element': '', 'hc_id': ''},
        follow_redirects=True
    )

    # Validate response redirects to sessions with an error
    assert response.status_code == 200
    assert b'Invalid exam request.' in response.data

@pytest.mark.usefixtures("app")
def test_ve_exam_results_in_progress_exam(client, ve_user):
    """Test ID: UT-247
    Test the ve_exam_results route when trying to review an exam that is still open.

    Asserts:
        - The response redirects to the sessions page with an appropriate error message.
    """
    # Set up mock exam and set it to open (in progress)
    pool, exam_session, exam, question, exam_answer = setup_mock_exam(ve_user)  # pylint: disable=W0612
    exam.open = True
    db.session.commit()

    # Log in as VE user
    response = login(client, ve_user.username, 'vepassword')
    assert response.status_code == 200

    # Attempt to review an in-progress exam
    response = client.post(
        url_for('main_ve.ve_exam_results'),
        data={'session_id': exam.session_id, 'exam_element': exam.element, 'hc_id': ve_user.id},
        follow_redirects=True
    )

    # Validate redirection to sessions page with an error message
    assert response.status_code == 200
    assert b'Exam is still in progress.' in response.data

@pytest.mark.usefixtures("app")
def test_ve_exam_results_invalid_exam(client, ve_user):
    """Test ID: UT-248
    Test the ve_exam_results route with an invalid exam ID.

    Asserts:
        - The response redirects to the sessions page with an error message.
    """
    # Log in as VE user
    response = login(client, ve_user.username, 'vepassword')
    assert response.status_code == 200

    # Attempt to review a non-existent exam
    response = client.post(
        url_for('main_ve.ve_exam_results'),
        data={'session_id': 999, 'exam_element': 2, 'hc_id': ve_user.id},
        follow_redirects=True
    )

    # Validate redirection with an error message
    assert response.status_code == 200
    assert b'Invalid exam ID.' in response.data

@pytest.mark.usefixtures("app")
def test_ve_exam_results_unauthorized_hc_access(client, ve_user):
    """Test ID: UT-249
    Test the ve_exam_results route when the VE tries to view results of another HC user.

    Asserts:
        - The response redirects to the sessions page with an error message.
    """
    # Set up mock exam with a different HC user
    pool, exam_session, exam, question, exam_answer = setup_mock_exam(ve_user)  # pylint: disable=W0612
    other_user_id = ve_user.id + 1  # Simulate another user
    exam.user_id = other_user_id
    db.session.commit()

    # Log in as VE user
    response = login(client, ve_user.username, 'vepassword')
    assert response.status_code == 200

    # Attempt to access results of a different HC
    response = client.post(
        url_for('main_ve.ve_exam_results'),
        data={'session_id': exam.session_id, 'exam_element': exam.element, 'hc_id': other_user_id},
        follow_redirects=True
    )

    # Validate redirection with error message
    assert response.status_code == 200
    assert b'Invalid HC ID.' in response.data
