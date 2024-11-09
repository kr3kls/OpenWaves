"""File: test_take_exam.py

    This file contains the tests for the take_exam code in the main.py file.
"""

from datetime import datetime
import pytest
from flask import url_for
from openwaves import db
from openwaves.imports import User, ExamSession, Exam, ExamAnswer, Pool, \
                            Question
from openwaves.tests.test_auth import login

def test_take_exam_role_not_allowed(client, ve_user):
    """Test ID: UT-194
    Negative test: Ensure that users with the VE role cannot access the take exam page.

    Args:
        client: The test client instance.

    Asserts:
        - The response status code is 302 (redirect).
        - The response redirects to the logout page.
        - An 'Access denied' message is flashed.
    """
    login(client, ve_user.username, 'vepassword')

    response = client.get(
        url_for('main.take_exam', exam_id=1),
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b'Access denied' in response.data

def test_take_exam_invalid_exam_id(client, app):
    """Test ID: UT-195
    Unit test to ensure that an invalid exam ID is handled correctly
    when trying to take an exam.

    This test simulates a user attempting to access an exam with a non-existent ID.

    Args:
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - Test user can log in successfully.
        - The exam retrieval fails due to an invalid ID.
        - Response data contains a flash message about the invalid exam ID.
        - The user is redirected to the sessions page.
    """
    with app.app_context():
        # Get the test user created by the fixture
        ham_user = User.query.filter_by(username="TESTUSER").first()

        # Log in as the test user
        response = login(client, ham_user.username, 'testpassword')
        assert response.status_code == 200

        # Send a GET request to access an exam with a non-existent ID (e.g., 9999)
        response = client.get(
            url_for('main.take_exam', exam_id=9999),
            follow_redirects=True
        )

        # Assert error message is flashed
        assert response.status_code == 200
        assert b"Invalid exam ID. Please try again." in response.data

        # Assert redirection to the sessions page
        assert b"Exam Sessions" in response.data

@pytest.mark.usefixtures("app")
def test_take_exam_post_save_answer(client, user_to_toggle):
    """Test ID: UT-209
    Test the take_exam route when saving a user's answer.

    This test simulates a POST request to the take_exam route and verifies that
    the user's answer is saved correctly to the database.

    Asserts:
        - The saved answer matches the provided answer.
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
        extra_pool_id=pool.id,
        status=True

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

    # Create a mock question
    question = Question(
        pool_id=pool.id,
        number='Q1',
        correct_answer=2,
        question='What is the frequency of the Tech license?',
        option_a='Option A',
        option_b='Option B',
        option_c='Option C',
        option_d='Option D',
        refs='Reference'
    )
    db.session.add(question)
    db.session.commit()

    # Create an exam answer
    exam_answer = ExamAnswer(
        exam_id=exam.id,
        question_id=question.id,
        question_number=1,
        answer=None,
        correct_answer=question.correct_answer
    )
    db.session.add(exam_answer)
    db.session.commit()

    # login user
    response = login(client, user_to_toggle.username, 'password')
    assert response.status_code == 200

    # Simulate a POST request to save an answer
    response = client.post(
        url_for('main.take_exam', exam_id=exam.id),
        data={'answer': '2', 'question_number': 1},
        follow_redirects=True
    )

    # Fetch the updated answer from the database
    updated_answer = ExamAnswer.query.filter_by(exam_id=exam.id, question_id=question.id).first()

    # Validate response and the saved answer
    assert response.status_code == 200
    print(response.data)
    assert updated_answer.answer == 2

@pytest.mark.usefixtures("app")
def test_take_exam_post_next_navigation(client, user_to_toggle):
    """Test ID: UT-210
    Test the take_exam route's "Next" navigation.

    This test simulates a POST request to navigate to the next question 
    in the exam.

    Asserts:
        - The current question index is incremented.
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
        extra_pool_id=pool.id,
        status=True
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

    # Create two questions for the exam
    questions = []
    for i in range(1, 3):  # Creating 2 questions
        question = Question(
            pool_id=pool.id,
            number=f'Q{i}',
            correct_answer=1,
            question=f'What is question {i}?',
            option_a='Option A',
            option_b='Option B',
            option_c='Option C',
            option_d='Option D',
            refs='Reference'
        )
        db.session.add(question)
        questions.append(question)
    db.session.commit()

    # Create exam answers for each question
    for i, question in enumerate(questions):
        exam_answer = ExamAnswer(
            exam_id=exam.id,
            question_id=question.id,
            question_number=i + 1,
            correct_answer=question.correct_answer,
            answer=None
        )
        db.session.add(exam_answer)
    db.session.commit()

    # Log in the user
    response = login(client, user_to_toggle.username, 'password')
    assert response.status_code == 200

    # Simulate a POST request for the "Next" navigation
    response = client.post(
        url_for('main.take_exam', exam_id=exam.id, index=0),
        data={'next': 'Next', 'question_number': 1},
        follow_redirects=True
    )

    # Check if the response contains the incremented index
    assert response.status_code == 200
    assert b'index=1' in response.data

@pytest.mark.usefixtures("app")
def test_take_exam_post_back_navigation(client, user_to_toggle):
    """Test ID: UT-211
    Test the take_exam route's "Back" navigation.

    This test simulates a POST request to navigate to the previous question 
    in the exam.

    Asserts:
        - The current question index is decremented.
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
        extra_pool_id=pool.id,
        status=True
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
        answer=None
    )
    db.session.add(exam_answer)
    db.session.commit()

    # login user
    response = login(client, user_to_toggle.username, 'password')
    assert response.status_code == 200

    # Simulate a POST request for the "Back" navigation
    response = client.post(
        url_for('main.take_exam', exam_id=exam.id, index=1),
        data={'back': 'Back', 'question_number': 1},
        follow_redirects=True
    )

    # Check if the response decrements the index
    assert response.status_code == 200
    assert b'index=0' in response.data

@pytest.mark.usefixtures("app")
def test_take_exam_post_review_navigation(client, user_to_toggle):
    """Test ID: UT-212
    Test the take_exam route's "Review" navigation.

    This test simulates a POST request to navigate to the review page.

    Asserts:
        - The response redirects to the review page.
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
        extra_pool_id=pool.id,
        status=True
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
        answer=None
    )
    db.session.add(exam_answer)
    db.session.commit()

    # login user
    response = login(client, user_to_toggle.username, 'password')
    assert response.status_code == 200

    # Simulate a POST request for the "Review" navigation
    response = client.post(
        url_for('main.take_exam', exam_id=exam.id),
        data={'review': 'Review', 'question_number': 1},
        follow_redirects=False
    )

    # Check if the response redirects to the review page
    assert response.status_code == 302
    assert url_for('main.review_exam', exam_id=exam.id) in response.location

@pytest.mark.usefixtures("app")
def test_take_exam_no_exam_found(client, user_to_toggle):
    """Test ID: UT-213
    Test the take_exam route when no exam is found.

    This test simulates a GET request to the take_exam route with an invalid exam ID.

    Asserts:
        - The response is redirected to the sessions page with an error message.
    """
    # login user
    response = login(client, user_to_toggle.username, 'password')
    assert response.status_code == 200

    response = client.get(url_for('main.take_exam', exam_id=999), follow_redirects=True)

    assert response.status_code == 200
    assert b'Invalid exam ID' in response.data

@pytest.mark.usefixtures("app")
def test_take_exam_get_first_question(client, user_to_toggle):
    """Test ID: UT-214
    Test the take_exam route when accessing the first question.

    This test ensures that the first question is loaded correctly 
    when the index is set to 0 or not provided.

    Asserts:
        - The first question is displayed.
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
        extra_pool_id=pool.id,
        status=True
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

    # Create a single question and commit it
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
        correct_answer=question.correct_answer
    )
    db.session.add(exam_answer)
    db.session.commit()

    # login user
    response = login(client, user_to_toggle.username, 'password')
    assert response.status_code == 200

    # Simulate a GET request for the first question (index=0)
    response = client.get(
        url_for('main.take_exam', exam_id=exam.id, index=0),
        follow_redirects=True
    )

    assert response.status_code == 200
    print(response.data)
    assert b'index=0' in response.data

@pytest.mark.usefixtures("app")
def test_take_exam_get_last_question(client, user_to_toggle):
    """Test ID: UT-215
    Test the take_exam route when accessing the last question.

    This test ensures that the last question is loaded correctly when 
    the index is set to the maximum number of questions.

    Asserts:
        - The last question is displayed.
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
        extra_pool_id=pool.id,
        status=True
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

    # Create multiple mock questions and commit them
    questions = []
    for i in range(1, 11):  # Simulating 10 questions
        question = Question(
            pool_id=pool.id,
            number=f'Q{i}',
            correct_answer=1,
            question=f'What is question {i}?',
            option_a='Option A',
            option_b='Option B',
            option_c='Option C',
            option_d='Option D',
            refs='Reference'
        )
        db.session.add(question)
        questions.append(question)
    db.session.commit()

    # Create exam answers for each question
    exam_answers = []
    for i, question in enumerate(questions):
        exam_answer = ExamAnswer(
            exam_id=exam.id,
            question_id=question.id,  # Use the committed question ID
            question_number=i + 1,
            correct_answer=question.correct_answer
        )
        db.session.add(exam_answer)
        exam_answers.append(exam_answer)
    db.session.commit()

    # login user
    response = login(client, user_to_toggle.username, 'password')
    assert response.status_code == 200

    # Simulate a GET request for the last question index
    response = client.get(
        url_for('main.take_exam', exam_id=exam.id, index=9),
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b'index=9' in response.data

@pytest.mark.usefixtures("app")
def test_take_exam_invalid_method(client):
    """Test ID: UT-216
    Test the take_exam route when an invalid method is used.

    This test ensures that only GET and POST methods are allowed.

    Asserts:
        - The response is a 405 Method Not Allowed error.
    """
    response = client.put(url_for('main.take_exam', exam_id=1), follow_redirects=True)

    assert response.status_code == 405
