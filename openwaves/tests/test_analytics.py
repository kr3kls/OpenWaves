"""File: test_analytics.py

    This file contains the tests for the analytics code in the main_ve.py file.
"""
from datetime import datetime
import pytest
from flask import url_for
from openwaves.imports import db, Pool, Question, ExamAnswer, Exam
from openwaves.tests.test_auth import login

@pytest.mark.usefixtures("app")
def test_data_analytics_authorized_access(client, ve_user):
    """Test ID: UT-273
    Test the data_analytics route with an authorized VE user having role 2.

    Asserts:
        - The response status code is 200.
        - The page contains analytics data for the selected pool.
    """
    # Set up mock pool and question data
    pool = Pool(name="General Pool",
                element=2,
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 12, 31))
    db.session.add(pool)
    db.session.commit()

    question = Question(
        pool_id=pool.id,
        number="G1A01",
        correct_answer=1,
        question="Sample Question",
        option_a="A",
        option_b="B",
        option_c="C",
        option_d="D"
    )
    db.session.add(question)
    db.session.commit()

    # Add an ExamAnswer to populate analytics data
    answer = ExamAnswer(
        exam_id=1,
        question_id=question.id,
        question_number=1,
        correct_answer=1,
        answer=2
    )
    db.session.add(answer)
    db.session.commit()

    # Log in as VE user with role 2
    response = login(client, ve_user.username, 'vepassword')
    assert response.status_code == 200

    # Simulate a GET request to data analytics route
    response = client.get(url_for('main_ve.data_analytics', pool_id=pool.id))
    assert response.status_code == 200
    assert b"Sample Question" in response.data

@pytest.mark.usefixtures("app")
def test_data_analytics_unauthorized_access(client, user_to_toggle):
    """Test ID: UT-274
    Test the data_analytics route with an unauthorized user (role not equal to 2).

    Asserts:
        - The response redirects to the logout page with an access denied message.
    """
    # Log in as user without VE privileges
    response = login(client, user_to_toggle.username, 'password')
    assert response.status_code == 200

    # Attempt to access the data analytics page
    response = client.get(url_for('main_ve.data_analytics'), follow_redirects=True)

    # Validate redirection to the logout page
    assert response.status_code == 200
    assert b"Access Denied" in response.data

@pytest.mark.usefixtures("app")
def test_data_analytics_empty_pool(client, ve_user):
    """Test ID: UT-275
    Test the data_analytics route with a pool that has no questions.

    Asserts:
        - The response status code is 200.
        - The page displays a message indicating no analytics data.
    """
    # Set up an empty mock pool with required fields
    pool = Pool(
        name="Empty Pool",
        element=2,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    db.session.add(pool)
    db.session.commit()

    # Log in as VE user
    response = login(client, ve_user.username, 'vepassword')
    assert response.status_code == 200

    # Simulate a GET request to the analytics page for the empty pool
    response = client.get(url_for('main_ve.data_analytics', pool_id=pool.id))
    assert response.status_code == 200

    # Check for the expected message indicating no analytics data is available
    assert b"No analytics data found for this pool." in response.data

@pytest.mark.usefixtures("app")
def test_data_analytics_incorrect_answers_aggregation(client, ve_user):
    """Test ID: UT-276
    Test the data_analytics route to verify aggregation of incorrect answers.

    Asserts:
        - The page displays the most missed question and incorrect answer selections.
    """
    # Set up mock pool with necessary fields
    pool = Pool(
        name="Advanced Pool",
        element=3,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    db.session.add(pool)
    db.session.commit()

    # Create a question in the pool
    question = Question(
        pool_id=pool.id,
        number="G2B01",
        correct_answer=1,
        question="Difficult Question",
        option_a="A",
        option_b="B",
        option_c="C",
        option_d="D"
    )
    db.session.add(question)
    db.session.commit()

    # Create an exam associated with the pool for completeness
    exam = Exam(
        user_id=ve_user.id,
        pool_id=pool.id,
        session_id=1,
        element=3,
        open=False
    )
    db.session.add(exam)
    db.session.commit()

    # Add an incorrect answer for the question in the exam
    incorrect_answer = ExamAnswer(
        exam_id=exam.id,
        question_id=question.id,
        question_number=1,
        correct_answer=1,
        answer=2
    )
    db.session.add(incorrect_answer)
    db.session.commit()

    # Log in as VE user
    response = login(client, ve_user.username, 'vepassword')
    assert response.status_code == 200

    # Simulate GET request to view analytics for the pool
    response = client.get(url_for('main_ve.data_analytics', pool_id=pool.id))
    assert response.status_code == 200

    # Check if the data is correctly rendered
    assert b"Difficult Question" in response.data
    assert b"Most Selected Wrong Answer" in response.data
    assert b"B" in response.data

@pytest.mark.usefixtures("app")
def test_data_analytics_no_pool_selected(client, ve_user):
    """Test ID: UT-277
    Test the data_analytics route when no pool is selected.

    Asserts:
        - The response status code is 200.
        - The page shows options to select a pool without displaying analytics data.
    """
    # Log in as VE user
    response = login(client, ve_user.username, 'vepassword')
    assert response.status_code == 200

    # Simulate GET request without pool_id parameter
    response = client.get(url_for('main_ve.data_analytics'))
    assert response.status_code == 200
    assert b"Please select a question pool to view analytics." in response.data

@pytest.mark.usefixtures("app")
def test_data_analytics_invalid_pool_id(client, ve_user):
    """Test ID: UT-278
    Test the data_analytics route with an invalid pool ID.

    Asserts:
        - The response status code is 200.
        - The page shows a message indicating no data available.
    """
    # Log in as VE user
    response = login(client, ve_user.username, 'vepassword')
    assert response.status_code == 200

    # Simulate GET request with invalid pool_id
    response = client.get(url_for('main_ve.data_analytics', pool_id=999))
    assert response.status_code == 200
    assert b"No analytics data available" in response.data

@pytest.mark.usefixtures("app")
def test_data_analytics_no_incorrect_answers(client, ve_user):
    """Test ID: UT-279
    Test the data_analytics route with questions in the pool but no incorrect answers.

    Asserts:
        - The response status code is 200.
        - The page indicates no analytics data due to lack of incorrect answers.
    """
    # Set up a pool with required fields
    pool = Pool(
        name="General Pool",
        element=1,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    db.session.add(pool)
    db.session.commit()

    # Add a question to the pool without any associated answers
    question = Question(
        pool_id=pool.id,
        number="Q1A01",
        correct_answer=1,
        question="Sample Question",
        option_a="A",
        option_b="B",
        option_c="C",
        option_d="D"
    )
    db.session.add(question)
    db.session.commit()

    # Mock an Exam entry linked to the pool but with no ExamAnswer entries
    exam = Exam(
        user_id=ve_user.id,
        pool_id=pool.id,
        session_id=1,
        element=1,
        open=False
    )
    db.session.add(exam)
    db.session.commit()

    # Log in as VE user
    response = login(client, ve_user.username, 'vepassword')
    assert response.status_code == 200

    # Simulate GET request for the pool analytics with no incorrect answers
    response = client.get(url_for('main_ve.data_analytics', pool_id=pool.id))
    assert response.status_code == 200
    assert b"No analytics data found for this pool." in response.data

@pytest.mark.usefixtures("app")
def test_data_analytics_mixed_correct_incorrect_answers(client, ve_user):
    """Test ID: UT-280
    Test the data_analytics route with a mix of correct and incorrect answers.

    Asserts:
        - Only incorrect answers are aggregated in the analytics data.
    """
    # Set up pool with required fields and a question
    pool = Pool(
        name="General Pool",
        element=1,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    db.session.add(pool)
    db.session.commit()

    question = Question(
        pool_id=pool.id,
        number="Q1A01",
        correct_answer=1,
        question="Challenging Question",
        option_a="A",
        option_b="B",
        option_c="C",
        option_d="D"
    )
    db.session.add(question)
    db.session.commit()

    # Mock an Exam entry for ExamAnswer records
    exam = Exam(
        user_id=ve_user.id,
        pool_id=pool.id,
        session_id=1,
        element=1,
        open=False
    )
    db.session.add(exam)
    db.session.commit()

    # Add both correct and incorrect answers, including a valid `exam_id` and `question_number`
    correct_answer = ExamAnswer(
        exam_id=exam.id,
        question_id=question.id,
        question_number=1,
        correct_answer=1,
        answer=1
    )
    incorrect_answer = ExamAnswer(
        exam_id=exam.id,
        question_id=question.id,
        question_number=1,
        correct_answer=1,
        answer=2
    )
    db.session.add_all([correct_answer, incorrect_answer])
    db.session.commit()

    # Log in as VE user
    response = login(client, ve_user.username, 'vepassword')
    assert response.status_code == 200

    # Simulate GET request for pool analytics
    response = client.get(url_for('main_ve.data_analytics', pool_id=pool.id))
    assert response.status_code == 200
    assert b"Challenging Question" in response.data
    assert b"Most Selected Wrong Answer" in response.data
    assert b"C - Selected 1 times" in response.data

@pytest.mark.usefixtures("app")
def test_data_analytics_multiple_pools(client, ve_user):
    """Test ID: UT-281
    Test the data_analytics route with multiple pools to ensure data separation.

    Asserts:
        - Data for each pool is kept separate in analytics display.
    """
    # Set up two pools with different questions, adding required fields
    pool1 = Pool(
        name="Pool One",
        element=1,  # Set a valid element number
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    pool2 = Pool(
        name="Pool Two",
        element=2,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    db.session.add_all([pool1, pool2])
    db.session.commit()

    # Add questions to each pool
    question1 = Question(
        pool_id=pool1.id,
        number="Q1A01",
        correct_answer=1,
        question="Question in Pool 1",
        option_a="A",
        option_b="B",
        option_c="C",
        option_d="D"
    )
    question2 = Question(
        pool_id=pool2.id,
        number="Q2A01",
        correct_answer=2,
        question="Question in Pool 2",
        option_a="A",
        option_b="B",
        option_c="C",
        option_d="D"
    )
    db.session.add_all([question1, question2])
    db.session.commit()

    # Create a mock exam for each pool to link with answers
    exam1 = Exam(user_id=ve_user.id, pool_id=pool1.id, session_id=1, element=1, open=False)
    exam2 = Exam(user_id=ve_user.id, pool_id=pool2.id, session_id=2, element=2, open=False)
    db.session.add_all([exam1, exam2])
    db.session.commit()

    # Add ExamAnswer instances to simulate answer data
    exam_answer1 = ExamAnswer(
        exam_id=exam1.id,
        question_id=question1.id,
        question_number=1,
        correct_answer=1,
        answer=2
    )
    exam_answer2 = ExamAnswer(
        exam_id=exam2.id,
        question_id=question2.id,
        question_number=1,
        correct_answer=2,
        answer=1
    )
    db.session.add_all([exam_answer1, exam_answer2])
    db.session.commit()

    # Log in as VE user
    response = login(client, ve_user.username, 'vepassword')
    assert response.status_code == 200

    # Verify pool 1 shows only its question
    response = client.get(url_for('main_ve.data_analytics', pool_id=pool1.id))
    assert response.status_code == 200
    assert b"Question in Pool 1" in response.data
    assert b"Question in Pool 2" not in response.data

    # Verify pool 2 shows only its question
    response = client.get(url_for('main_ve.data_analytics', pool_id=pool2.id))
    assert response.status_code == 200
    assert b"Question in Pool 2" in response.data
    assert b"Question in Pool 1" not in response.data

@pytest.mark.usefixtures("app")
def test_data_analytics_sorting_consistency(client, ve_user):
    """Test ID: UT-282
    Test the data_analytics sorting by miss count for consistent top 5 selection.

    Asserts:
        - The top missed questions are sorted correctly by miss count.
    """
    # Set up pool and questions with varied miss counts
    pool = Pool(
        name="Sorted Pool",
        element=1,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    db.session.add(pool)
    db.session.commit()

    # Create a mock exam for this pool
    exam = Exam(
        user_id=ve_user.id,
        pool_id=pool.id,
        session_id=1,
        element=1,
        open=False
    )
    db.session.add(exam)
    db.session.commit()

    questions = [
        Question(pool_id=pool.id,
                 number=f"E{i}A01",
                 correct_answer=1,
                 question=f"Question {i}",
                 option_a="A",
                 option_b="B",
                 option_c="C",
                 option_d="D")
        for i in range(10)
    ]
    db.session.add_all(questions)
    db.session.commit()

    # Add incorrect answers with increasing miss counts
    for i, question in enumerate(questions, 1):
        incorrect_answers = [
            ExamAnswer(
                exam_id=exam.id,
                question_id=question.id,
                question_number=i,
                answer=2,
                correct_answer=1
            )
            for _ in range(i)
        ]
        db.session.add_all(incorrect_answers)
    db.session.commit()

    # Log in as VE user
    response = login(client, ve_user.username, 'vepassword')
    assert response.status_code == 200

    # Verify sorted response for top 5 missed questions
    response = client.get(url_for('main_ve.data_analytics', pool_id=pool.id))
    assert response.status_code == 200
    top_questions = [f"Question {i}" for i in range(5, 10)]
    for question_text in top_questions:
        assert question_text.encode() in response.data
