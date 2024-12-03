"""File: test_ve_results.py

    This file contains the unit tests for the ve exam results code in the main_ve.py file.
"""

from datetime import datetime
import pytest
from flask import url_for
from openwaves.imports import db, ExamSession, Pool
from openwaves.tests.test_unit_auth import login
from openwaves.tests.test_integration_review_exam import setup_mock_exam

@pytest.mark.usefixtures("app")
def test_ve_exam_results_unauthorized_role(client, user_to_toggle):
    """Test ID: UT-63
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
    """Test ID: UT-64
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
def test_ve_exam_results_invalid_exam(client, ve_user):
    """Test ID: UT-65
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
    """Test ID: UT-66
    Test the ve_exam_results route when the VE tries to view results of another HC user.

    Asserts:
        - The response redirects to the sessions page with an error message.
    """
    # Set up mock exam with a different HC user
    pool, exam_session, exam, question, exam_answer = setup_mock_exam(ve_user)  # pylint: disable=W0612
    other_user_id = ve_user.id + 1
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

@pytest.mark.usefixtures("app")
def test_ve_session_results_unauthorized_role(client, user_to_toggle):
    """Test ID: UT-67
    Test the ve_session_results route with an unauthorized user role.

    Asserts:
        - The response redirects to the logout page.
    """
    # Create a mock pool (required for tech_pool_id, gen_pool_id, extra_pool_id)
    pool = Pool(
        name="Tech Pool",
        element=2,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    db.session.add(pool)
    db.session.commit()

    # Create a mock session using the pool IDs
    session = ExamSession(
        session_date=datetime(2024, 10, 1),
        tech_pool_id=pool.id,
        gen_pool_id=pool.id,
        extra_pool_id=pool.id,
        status=False
    )
    db.session.add(session)
    db.session.commit()

    # Log in as an unauthorized user
    response = login(client, user_to_toggle.username, 'password')
    assert response.status_code == 200

    # Attempt to access the session results page
    response = client.get(
        url_for('main_ve.ve_session_results', session_id=session.id),
        follow_redirects=False
    )

    # Check if the response redirects to the logout page
    assert response.status_code == 302
    assert url_for('auth.logout') in response.location

@pytest.mark.usefixtures("app")
def test_ve_session_results_invalid_session(client, ve_user):
    """Test ID: UT-68
    Test the ve_session_results route with an invalid session ID.

    Asserts:
        - The response redirects to the sessions page with an error message.
    """
    # Log in as the VE user
    response = login(client, ve_user.username, 'vepassword')
    assert response.status_code == 200

    # Attempt to access a non-existent session results page
    response = client.get(
        url_for('main_ve.ve_session_results', session_id=999),
        follow_redirects=True
    )

    # Validate redirection to the sessions page with an error message
    assert response.status_code == 200
    assert b'Session not found.' in response.data
