"""File: test_ve_results.py

    This file contains the integration tests for the ve exam results code in the main_ve.py file.
"""

from datetime import datetime
import pytest
from flask import url_for
from openwaves.imports import db, ExamSession, Pool, User, Exam, ExamAnswer
from openwaves.tests.test_unit_auth import login
from openwaves.tests.test_integration_review_exam import setup_mock_exam

@pytest.mark.usefixtures("app")
def test_ve_exam_results_in_progress_exam(client, ve_user):
    """Test ID: IT-134
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
def test_ve_session_results_authorized(client, ve_user):
    """Test ID: IT-135
    Test the ve_session_results route with an authorized VE user.

    Asserts:
        - The response status code is 200.
        - The response contains exam results for the session.
    """
    # Set up mock data for the pool and session
    pool = Pool(
        name="Tech Pool",
        element=2,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    db.session.add(pool)
    db.session.commit()

    # Create a mock session
    session = ExamSession(
        session_date=datetime(2024, 10, 1),
        tech_pool_id=pool.id,
        gen_pool_id=pool.id,
        extra_pool_id=pool.id,
        status=False
    )
    db.session.add(session)
    db.session.commit()

    # Create a user and exam for the session
    hc_user = User(
        username="hc_user",
        first_name="John",
        last_name="Doe",
        email="hc_user@example.com",
        password="password",
        role=1
    )
    db.session.add(hc_user)
    db.session.commit()

    exam = Exam(
        user_id=hc_user.id,
        session_id=session.id,
        element=2,
        pool_id=pool.id,
        open=False
    )
    db.session.add(exam)
    db.session.commit()

    # Create exam answers for the exam
    answer1 = ExamAnswer(exam_id=exam.id,
                         question_id=1,
                         question_number=1,
                         correct_answer=1,
                         answer=1)
    answer2 = ExamAnswer(exam_id=exam.id,
                         question_id=2,
                         question_number=2,
                         correct_answer=1,
                         answer=2)
    db.session.add_all([answer1, answer2])
    db.session.commit()

    # Log in as the VE user
    response = login(client, ve_user.username, 'vepassword')
    assert response.status_code == 200

    # Simulate a GET request to view session results
    response = client.get(
        url_for('main_ve.ve_session_results', session_id=session.id),
        follow_redirects=True
    )

    # Validate response and check if the results data is present
    assert response.status_code == 200
    assert b'John' in response.data
    assert b'Doe' in response.data
    assert b'26' in response.data or b'Pass' in response.data

@pytest.mark.usefixtures("app")
def test_ve_session_results_no_exams(client, ve_user):
    """Test ID: IT-136
    Test the ve_session_results route with a session that has no exams.

    Asserts:
        - The response status code is 200.
        - The page indicates that no exam results are available.
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

    # Create a mock session with required pool IDs but no exams
    session = ExamSession(
        session_date=datetime(2024, 10, 1),
        tech_pool_id=pool.id,
        gen_pool_id=pool.id,
        extra_pool_id=pool.id,
        status=False
    )
    db.session.add(session)
    db.session.commit()

    # Log in as VE user
    response = login(client, ve_user.username, 'vepassword')
    assert response.status_code == 200

    # Simulate a GET request to view session results
    response = client.get(
        url_for('main_ve.ve_session_results', session_id=session.id),
        follow_redirects=True
    )

    # Validate response
    assert response.status_code == 200
    assert b'No exam results found.' in response.data

@pytest.mark.usefixtures("app")
def test_ve_session_results_pass_fail_logic(client, ve_user):
    """Test ID: IT-137
    Test the ve_session_results route to verify pass/fail logic.

    Asserts:
        - The exam results indicate correct pass/fail status based on score.
    """
    # Set up mock data for the pool and session
    pool = Pool(
        name="Extra Pool",
        element=4,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    db.session.add(pool)
    db.session.commit()

    # Create a mock session
    session = ExamSession(
        session_date=datetime(2024, 10, 1),
        tech_pool_id=pool.id,
        gen_pool_id=pool.id,
        extra_pool_id=pool.id,
        status=False
    )
    db.session.add(session)
    db.session.commit()

    # Create a user and exam for the session
    hc_user = User(
        username="hc_user",
        first_name="Alice",
        last_name="Smith",
        email="alice_smith@example.com",
        password="password",
        role=1
    )
    db.session.add(hc_user)
    db.session.commit()

    exam = Exam(
        user_id=hc_user.id,
        session_id=session.id,
        element=4,
        pool_id=pool.id,
        open=False
    )
    db.session.add(exam)
    db.session.commit()

    # Add exam answers to simulate score
    correct_answers = [ExamAnswer(exam_id=exam.id,
                                  question_id=i,
                                  question_number=i,
                                  correct_answer=1,
                                  answer=1) for i in range(1, 38)]
    db.session.add_all(correct_answers)
    db.session.commit()

    # Log in as the VE user
    response = login(client, ve_user.username, 'vepassword')
    assert response.status_code == 200

    # Simulate a GET request to view session results
    response = client.get(
        url_for('main_ve.ve_session_results', session_id=session.id),
        follow_redirects=True
    )

    # Validate response and pass/fail status
    assert response.status_code == 200
    assert b'Alice' in response.data
    assert b'Smith' in response.data
    assert b'Pass' in response.data

@pytest.mark.usefixtures("app")
def test_ve_exam_results_valid_request(client, ve_user):
    """Test ID: IT-138
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
    assert b'Score: 1/35' in response.data
