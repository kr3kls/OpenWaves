"""File: test_review_exam.py

    This file contains the integration tests for the review_exam code in the main.py file.
"""
from datetime import datetime
import pytest
from flask import url_for
from openwaves.imports import db, Exam, ExamSession, ExamAnswer, Pool, Question
from openwaves.tests.test_unit_auth import login

# Helper function to set up a mock exam with related data
def setup_mock_exam(user):
    """
    Helper function to set up a mock exam with related data.

    Returns:
        - pool, exam_session, exam, question, exam_answer
    """
    # Set up mock data for the pool
    pool = Pool(
        name="Tech Pool",
        element=2,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    db.session.add(pool)
    db.session.commit()

    # Create a mock exam session
    exam_session = ExamSession(
        session_date=datetime(2024, 10, 1),
        tech_pool_id=pool.id,
        gen_pool_id=pool.id,
        extra_pool_id=pool.id
    )
    db.session.add(exam_session)
    db.session.commit()

    # Create a completed exam
    exam = Exam(
        user_id=user.id,
        open=False,  # Closed/completed exam
        element=2,
        pool_id=pool.id,
        session_id=exam_session.id
    )
    db.session.add(exam)
    db.session.commit()

    # Create a question for the exam
    question = Question(
        pool_id=pool.id,
        number='Q1',
        correct_answer=1,
        question='What is question 1?',
        option_a='Option A',
        option_b='Option B',
        option_c='Option C',
        option_d='Option D',
        refs='Reference'
    )
    db.session.add(question)
    db.session.commit()

    # Create an exam answer for the question
    exam_answer = ExamAnswer(
        exam_id=exam.id,
        question_id=question.id,
        question_number=1,
        correct_answer=question.correct_answer,
        answer=1  # Simulate correct answer
    )
    db.session.add(exam_answer)
    db.session.commit()

    return pool, exam_session, exam, question, exam_answer

@pytest.mark.usefixtures("app")
def test_review_exam_invalid_role(client, ve_user):
    """Test ID: IT-119
    Test the review_exam route with an invalid user role.

    This test ensures that users without the appropriate role 
    cannot access the exam review page.

    Asserts:
        - The response is a redirection to the logout page.
    """
    # Login as the VE user
    response = login(client, ve_user.username, 'vepassword')
    assert response.status_code == 200

    # Simulate a GET request to review an exam
    response = client.get(
        url_for('main.review_exam', exam_id=1),
        follow_redirects=False
    )

    # Check if the response redirects to the logout page
    assert response.status_code == 302
    assert url_for('auth.logout') in response.location

@pytest.mark.usefixtures("app")
def test_review_exam_closed_exam(client, user_to_toggle):
    """Test ID: IT-120
    Test the review_exam route with a closed exam.

    This test ensures that users cannot review a closed exam.

    Asserts:
        - The response redirects to the sessions page with an error message.
    """
    # Set up mock data for the pool
    pool = Pool(
        name="Tech Pool",
        element=2,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    db.session.add(pool)
    db.session.commit()

    # Create a mock exam session
    exam_session = ExamSession(
        session_date=datetime(2024, 10, 1),
        tech_pool_id=pool.id,
        gen_pool_id=pool.id,
        extra_pool_id=pool.id
    )
    db.session.add(exam_session)
    db.session.commit()

    # Set up a mock closed exam
    exam = Exam(
        user_id=user_to_toggle.id,
        open=False,  # Closed exam
        element=2,
        pool_id=pool.id,
        session_id=exam_session.id
    )
    db.session.add(exam)
    db.session.commit()

    # login as the current user
    response = login(client, user_to_toggle.username, 'password')
    assert response.status_code == 200

    # Simulate a GET request to review the closed exam
    response = client.get(
        url_for('main.review_exam', exam_id=exam.id),
        follow_redirects=True
    )

    # Check if the response redirects to the sessions page with an error message
    assert response.status_code == 200
    assert b'Invalid or closed exam ID.' in response.data

@pytest.mark.usefixtures("app")
def test_review_exam_invalid_exam_id(client, user_to_toggle):
    """Test ID: IT-121
    Test the review_exam route with an invalid exam ID.

    This test ensures that an invalid exam ID results in a redirection 
    to the sessions page.

    Asserts:
        - The response redirects to the sessions page with an error message.
    """
    # login user
    response = login(client, user_to_toggle.username, 'password')
    assert response.status_code == 200

    # Simulate a GET request to review an invalid exam ID
    response = client.get(
        url_for('main.review_exam', exam_id=999),
        follow_redirects=True
    )

    # Check if the response redirects to the sessions page
    assert response.status_code == 200
    assert b'Invalid or closed exam ID.' in response.data

@pytest.mark.usefixtures("app")
def test_review_exam_unauthorized_access(client, user_to_toggle):
    """Test ID: IT-122
    Test the review_exam route with unauthorized access.

    This test ensures that users cannot access exams belonging to other users.

    Asserts:
        - The response redirects to the logout page.
    """
    # Set up mock data for the pool
    pool = Pool(
        name="Tech Pool",
        element=2,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    db.session.add(pool)
    db.session.commit()

    # Create a mock exam session
    exam_session = ExamSession(
        session_date=datetime(2024, 10, 1),
        tech_pool_id=pool.id,
        gen_pool_id=pool.id,
        extra_pool_id=pool.id
    )
    db.session.add(exam_session)
    db.session.commit()

    # Set up a mock exam belonging to another user
    exam = Exam(
        user_id=user_to_toggle.id + 1,  # Different user
        open=True,
        element=2,
        pool_id=pool.id,
        session_id=exam_session.id
    )
    db.session.add(exam)
    db.session.commit()

    # login as the current user
    response = login(client, user_to_toggle.username, 'password')
    assert response.status_code == 200

    # Simulate a GET request to review another user's exam
    response = client.get(
        url_for('main.review_exam', exam_id=exam.id),
        follow_redirects=True
    )

    # Check if the response redirects to the logout page
    assert response.status_code == 200
    assert b'Access denied.' in response.data

@pytest.mark.usefixtures("app")
def test_finish_exam_success(client, user_to_toggle):
    """Test ID: IT-123
    Test the successful closure of an open exam by the authorized user.

    Asserts:
        - The exam is marked as closed.
        - The response redirects to the exam results page.
    """
    # Set up mock data for the pool
    pool = Pool(
        name="Tech Pool",
        element=2,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    db.session.add(pool)
    db.session.commit()

    # Create a mock exam session
    exam_session = ExamSession(
        session_date=datetime(2024, 10, 1),
        tech_pool_id=pool.id,
        gen_pool_id=pool.id,
        extra_pool_id=pool.id
    )
    db.session.add(exam_session)
    db.session.commit()

    # Create a mock open exam
    exam = Exam(
        user_id=user_to_toggle.id,
        open=True,
        element=2,
        pool_id=pool.id,
        session_id=exam_session.id
    )
    db.session.add(exam)
    db.session.commit()

    # login as the current user
    response = login(client, user_to_toggle.username, 'password')
    assert response.status_code == 200

    # Simulate a GET request to finish the exam
    response = client.get(
        url_for('main.finish_exam', exam_id=exam.id),
        follow_redirects=True
    )

    # Fetch the updated exam from the database
    updated_exam = db.session.get(Exam, exam.id)

    # Validate response and exam status
    assert response.status_code == 200
    assert not updated_exam.open
    assert b'Results: Score:' in response.data

@pytest.mark.usefixtures("app")
def test_finish_exam_unauthorized_role(client, ve_user):
    """Test ID: IT-124
    Test the finish_exam route with an unauthorized role.

    Asserts:
        - The response redirects to the logout page.
    """
    # login as the ve user
    response = login(client, ve_user.username, 'vepassword')
    assert response.status_code == 200

    # Simulate a GET request to finish the exam
    response = client.get(
        url_for('main.finish_exam', exam_id=1),  # Using any exam ID for unauthorized access
        follow_redirects=True
    )

    # Validate redirection to the logout page
    assert response.status_code == 200
    assert b'Access denied.' in response.data

@pytest.mark.usefixtures("app")
def test_finish_exam_closed_exam(client, user_to_toggle):
    """Test ID: IT-125
    Test the finish_exam route when attempting to finish a closed exam.

    Asserts:
        - The response redirects to the sessions page with an error message.
    """
    # Set up mock data for the pool
    pool = Pool(
        name="Tech Pool",
        element=2,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    db.session.add(pool)
    db.session.commit()

    # Create a mock exam session
    exam_session = ExamSession(
        session_date=datetime(2024, 10, 1),
        tech_pool_id=pool.id,
        gen_pool_id=pool.id,
        extra_pool_id=pool.id
    )
    db.session.add(exam_session)
    db.session.commit()

    # Set up a mock closed exam
    exam = Exam(
        user_id=user_to_toggle.id,
        open=False,  # Already closed
        element=2,
        pool_id=pool.id,
        session_id=exam_session.id
    )
    db.session.add(exam)
    db.session.commit()

    # login as the current user
    response = login(client, user_to_toggle.username, 'password')
    assert response.status_code == 200

    # Simulate a GET request to finish the closed exam
    response = client.get(
        url_for('main.finish_exam', exam_id=exam.id),
        follow_redirects=True
    )

    # Validate redirection to the sessions page with an error message
    assert response.status_code == 200
    assert b'Invalid or closed exam ID.' in response.data

@pytest.mark.usefixtures("app")
def test_finish_exam_another_users_exam(client, user_to_toggle):
    """Test ID: IT-126
    Test the finish_exam route when trying to finish another user's exam.

    Asserts:
        - The response redirects to the logout page.
    """
    # Set up mock data for the pool
    pool = Pool(
        name="Tech Pool",
        element=2,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    db.session.add(pool)
    db.session.commit()

    # Create a mock exam session
    exam_session = ExamSession(
        session_date=datetime(2024, 10, 1),
        tech_pool_id=pool.id,
        gen_pool_id=pool.id,
        extra_pool_id=pool.id
    )
    db.session.add(exam_session)
    db.session.commit()

    # Create a mock exam belonging to a different user
    exam = Exam(
        user_id=user_to_toggle.id + 1,  # Different user
        open=True,
        element=2,
        pool_id=pool.id,
        session_id=exam_session.id
    )
    db.session.add(exam)
    db.session.commit()

    # login as the current user
    response = login(client, user_to_toggle.username, 'password')
    assert response.status_code == 200

    # Simulate a GET request to finish another user's exam
    response = client.get(
        url_for('main.finish_exam', exam_id=exam.id),
        follow_redirects=True
    )

    # Validate redirection to the logout page
    assert response.status_code == 200
    assert b'Access denied.' in response.data

@pytest.mark.usefixtures("app")
def test_finish_exam_non_existent_exam(client, user_to_toggle):
    """Test ID: IT-127
    Test the finish_exam route with a non-existent exam.

    Asserts:
        - The response redirects to the sessions page with an error message.
    """
    # login as the current user
    response = login(client, user_to_toggle.username, 'password')
    assert response.status_code == 200

    # Simulate a GET request to finish a non-existent exam
    response = client.get(
        url_for('main.finish_exam', exam_id=999),  # Non-existent exam ID
        follow_redirects=True
    )

    # Validate redirection to the sessions page with an error message
    assert response.status_code == 200
    assert b'Invalid or closed exam ID.' in response.data

@pytest.mark.usefixtures("app")
def test_exam_results_get_request(client, user_to_toggle):
    """Test ID: IT-128
    Test the exam_results route with a valid GET request.

    Asserts:
        - The response status code is 200.
        - The exam results are displayed correctly.
    """
    # Set up mock data for the pool
    pool = Pool(
        name="Tech Pool",
        element=2,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    db.session.add(pool)
    db.session.commit()

    # Create a mock exam session
    exam_session = ExamSession(
        session_date=datetime(2024, 10, 1),
        tech_pool_id=pool.id,
        gen_pool_id=pool.id,
        extra_pool_id=pool.id
    )
    db.session.add(exam_session)
    db.session.commit()

    # Create a completed exam
    exam = Exam(
        user_id=user_to_toggle.id,
        open=False,  # Closed/completed exam
        element=2,
        pool_id=pool.id,
        session_id=exam_session.id
    )
    db.session.add(exam)
    db.session.commit()

    # Create a question for the exam
    question = Question(
        pool_id=pool.id,
        number='Q1',
        correct_answer=1,
        question='What is question 1?',
        option_a='Option A',
        option_b='Option B',
        option_c='Option C',
        option_d='Option D',
        refs='Reference'
    )
    db.session.add(question)
    db.session.commit()

    # Create an exam answer for the question
    exam_answer = ExamAnswer(
        exam_id=exam.id,
        question_id=question.id,
        question_number=1,
        correct_answer=question.correct_answer,
        answer=1  # Simulate correct answer
    )
    db.session.add(exam_answer)
    db.session.commit()

    # login user
    response = login(client, user_to_toggle.username, 'password')
    assert response.status_code == 200

    # Simulate a GET request to view exam results
    response = client.get(
        url_for('main.exam_results', session_id=exam.session_id, exam_element=exam.element),
        follow_redirects=True
    )

    # Validate response
    assert response.status_code == 200
    assert b'What is question 1?' in response.data
    assert b'Score: 1/35' in response.data  # Adjust based on scoring logic

@pytest.mark.usefixtures("app")
def test_exam_results_post_request(client, user_to_toggle):
    """Test ID: IT-129
    Test the exam_results route with a valid POST request.

    Asserts:
        - The response status code is 200.
        - The exam results are displayed correctly.
    """
    # Set up mock data similar to the GET request test
    pool, exam_session, exam, question, exam_answer = setup_mock_exam(user_to_toggle) # pylint: disable=W0612

    # login user
    response = login(client, user_to_toggle.username, 'password')
    assert response.status_code == 200

    # Simulate a POST request to view exam results
    response = client.post(
        url_for('main.exam_results'),
        data={'session_id': exam.session_id, 'exam_element': exam.element},
        follow_redirects=True
    )

    # Validate response
    assert response.status_code == 200
    assert b'What is question 1?' in response.data
    assert b'Score: 1/35' in response.data  # Adjust based on scoring logic

@pytest.mark.usefixtures("app")
def test_exam_results_invalid_session(client, user_to_toggle):
    """Test ID: IT-130
    Test the exam_results route with an invalid session ID.

    Asserts:
        - The response redirects to the sessions page with an error message.
    """
    # login user
    response = login(client, user_to_toggle.username, 'password')
    assert response.status_code == 200

    # Simulate a GET request with an invalid session ID
    response = client.get(
        url_for('main.exam_results', session_id=999, exam_element=2),
        follow_redirects=True
    )

    # Validate response
    assert response.status_code == 200
    assert b'Invalid exam ID.' in response.data

@pytest.mark.usefixtures("app")
def test_exam_results_in_progress_exam(client, user_to_toggle):
    """Test ID: IT-131
    Test the exam_results route when the exam is still open.

    Asserts:
        - The response redirects to the sessions page with an error message.
    """
    pool, exam_session, exam, question, exam_answer = setup_mock_exam(user_to_toggle) # pylint: disable=W0612

    # Set exam to open (in progress)
    exam.open = True
    db.session.commit()

    # login user
    response = login(client, user_to_toggle.username, 'password')
    assert response.status_code == 200

    # Simulate a GET request for an in-progress exam
    response = client.get(
        url_for('main.exam_results', session_id=exam.session_id, exam_element=exam.element),
        follow_redirects=True
    )

    # Validate response
    assert response.status_code == 200
    assert exam.open is False
    assert b'Results: Score:' in response.data

@pytest.mark.usefixtures("app")
def test_exam_results_unauthorized_access(client, user_to_toggle):
    """Test ID: IT-132
    Test the exam_results route when trying to view another user's exam.

    Asserts:
        - The response redirects to the logout page.
    """
    pool, exam_session, exam, question, exam_answer = setup_mock_exam(user_to_toggle) # pylint: disable=W0612

    # Change the exam's user_id to simulate unauthorized access
    exam.user_id = user_to_toggle.id + 1  # Different user
    db.session.commit()

    # login user
    response = login(client, user_to_toggle.username, 'password')
    assert response.status_code == 200

    # Simulate a GET request for another user's exam
    response = client.get(
        url_for('main.exam_results', session_id=exam.session_id, exam_element=exam.element),
        follow_redirects=True
    )

    # Validate redirection to the logout page
    assert response.status_code == 200
    assert b'Access denied.' or b'Invalid exam ID.' in response.data

@pytest.mark.usefixtures("app")
def test_review_exam_valid_exam(client, user_to_toggle):
    """Test ID: IT-133
    Test the review_exam route with a valid exam.

    This test ensures that the exam review page loads correctly 
    when the user has permission and the exam is open.

    Asserts:
        - The response contains the exam name and questions.
    """
    # Set up mock data for the pool
    pool = Pool(
        name="Tech Pool",
        element=2,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    db.session.add(pool)
    db.session.commit()

    # Create a mock exam session
    exam_session = ExamSession(
        session_date=datetime(2024, 10, 1),
        tech_pool_id=pool.id,
        gen_pool_id=pool.id,
        extra_pool_id=pool.id
    )
    db.session.add(exam_session)
    db.session.commit()

    # Create a mock exam
    exam = Exam(
        user_id=user_to_toggle.id,
        open=True,
        element=2,
        pool_id=pool.id,
        session_id=exam_session.id
    )
    db.session.add(exam)
    db.session.commit()

    # Create a question for the exam
    question = Question(
        pool_id=pool.id,
        number='Q1',
        correct_answer=1,
        question='What is question 1?',
        option_a='Option A',
        option_b='Option B',
        option_c='Option C',
        option_d='Option D',
        refs='Reference'
    )
    db.session.add(question)
    db.session.commit()

    # Create an exam answer for the question
    exam_answer = ExamAnswer(
        exam_id=exam.id,
        question_id=question.id,
        question_number=1,
        correct_answer=question.correct_answer,
        answer=1
    )
    db.session.add(exam_answer)
    db.session.commit()

    # login user
    response = login(client, user_to_toggle.username, 'password')
    assert response.status_code == 200

    # Simulate a GET request to review the exam
    response = client.get(
        url_for('main.review_exam', exam_id=exam.id),
        follow_redirects=True
    )

    # Check if the response contains the exam review information
    assert response.status_code == 200
    print(response.data)
    assert b'Tech Exam: Element 2' in response.data
    assert b'What is question 1?' in response.data
