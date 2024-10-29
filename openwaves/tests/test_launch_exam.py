"""File: test_launch_exam.py

    This file contains the tests for the launch_exam code in the main.py file.
"""
from unittest.mock import patch
from io import BytesIO
from datetime import datetime
from flask import url_for
from sqlalchemy.exc import SQLAlchemyError
from openwaves import db
from openwaves.imports import User, ExamSession, ExamRegistration, Exam, ExamAnswer, Pool, \
                            get_exam_name
from openwaves.tests.test_auth import login, logout

def test_launch_exam_success(client, app, ve_user): # pylint: disable=R0914
    """Test ID: UT-185
    Functional test to ensure a new exam session is successfully created.

    This test verifies that a user with a valid registration can start an exam session,
    and that the appropriate number of questions are generated for the exam.

    Args:
        client: The test client instance.
        app: The Flask application instance.
        ve_user: The VE user fixture.

    Asserts:
        - VE user can upload questions to a pool successfully.
        - Test user can log in successfully.
        - Exam launch request returns a 200 status code.
        - Response data contains "Question ID".
        - The new exam is created with 35 questions in the database.
    """
    with app.app_context():
        # Get the test user created by the fixture
        ham_user = User.query.filter_by(username="TESTUSER").first()

        # Create pools for exam session
        tech_pool = Pool(name="Tech Pool",
                        element="2",
                        start_date=datetime.now(),
                        end_date=datetime.now())
        gen_pool = Pool(name="General Pool",
                        element="3",
                        start_date=datetime.now(),
                        end_date=datetime.now())
        extra_pool = Pool(name="Extra Pool",
                        element="4",
                        start_date=datetime.now(),
                        end_date=datetime.now())
        db.session.add(tech_pool)
        db.session.add(gen_pool)
        db.session.add(extra_pool)
        db.session.commit()
        tech_id = tech_pool.id
        gen_id = gen_pool.id
        extra_id = extra_pool.id

        # Prepare a CSV file-like object to upload
        csv_content = """id,correct,question,a,b,c,d,refs
T1A01,A,What is 1+1?,2,3,4,5,Reference1
T1B02,B,What is 2+2?,1,4,3,5,Reference2
T1C03,C,What is 3+3?,1,2,6,5,Reference3
T1D04,D,What is 4+4?,4,8,3,5,Reference4
T1E05,A,What is 5+5?,10,1,3,5,Reference5
T1F06,B,What is 6+6?,1,12,4,5,Reference6
T1G07,C,What is 7+7?,14,3,4,5,Reference7
T1H08,D,What is 8+8?,4,3,16,5,Reference8
T1I09,A,What is 9+9?,18,3,4,5,Reference9
T1J10,B,What is 10+10?,1,20,4,5,Reference10
T1K11,C,What is 11+11?,1,22,4,5,Reference11
T1L12,D,What is 12+12?,1,24,4,5,Reference12
T1M13,A,What is 13+13?,26,3,4,5,Reference13
T1N14,B,What is 14+14?,1,28,4,5,Reference14
T1O15,C,What is 15+15?,1,30,4,5,Reference15
T1P16,D,What is 16+16?,1,32,4,5,Reference16
T1Q17,A,What is 17+17?,34,3,4,5,Reference17
T1R18,B,What is 18+18?,1,36,4,5,Reference18
T1S19,C,What is 19+19?,1,38,4,5,Reference19
T1T20,D,What is 20+20?,1,40,4,5,Reference20
T1U21,A,What is 21+21?,42,3,4,5,Reference21
T1V22,B,What is 22+22?,1,44,4,5,Reference22
T1W23,C,What is 23+23?,1,46,4,5,Reference23
T1X24,D,What is 24+24?,1,48,4,5,Reference24
T1Y25,A,What is 25+25?,50,3,4,5,Reference25
T1Z26,B,What is 26+26?,1,52,4,5,Reference26
T2A27,C,What is 27+27?,1,54,4,5,Reference27
T2B28,D,What is 28+28?,1,56,4,5,Reference28
T2C29,A,What is 29+29?,58,3,4,5,Reference29
T2D30,B,What is 30+30?,1,60,4,5,Reference30
T2E31,C,What is 31+31?,1,62,4,5,Reference31
T2F32,D,What is 32+32?,1,64,4,5,Reference32
T2G33,A,What is 33+33?,66,3,4,5,Reference33
T2H34,B,What is 34+34?,1,68,4,5,Reference34
T2I35,C,What is 35+35?,1,70,4,5,Reference35
"""
        data = {
            'file': (BytesIO(csv_content.encode('utf-8')), 'questions.csv')
        }

        # Ensure a VE user is logged in
        login(client, ve_user.username, 'vepassword')

        response = client.post(f'/ve/upload_questions/{tech_id}',
                               data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        assert response.is_json
        assert response.get_json()['success'] is True

        # Logout ve_user
        logout(client)

        # Create a valid exam registration and session
        exam_session = ExamSession(
            session_date=datetime.today(),
            tech_pool_id=tech_id,
            gen_pool_id=gen_id,
            extra_pool_id=extra_id
        )
        db.session.add(exam_session)
        db.session.commit()

        exam_registration = ExamRegistration(
            user_id=ham_user.id,
            session_id=exam_session.id,
            tech=True,
            gen=False,
            extra=False,
            valid=True
        )
        db.session.add(exam_registration)
        db.session.commit()

        # Log in as the test user
        response = login(client, ham_user.username, 'testpassword')
        assert response.status_code == 200

        # Send POST request to launch exam
        response = client.post(
            url_for('main.launch_exam'),
            data={
                'session_id': exam_session.id,
                'exam_element': '2',
                'exam_name': get_exam_name('2')
            },
            follow_redirects=True
        )
        # Assert redirection to 'take_exam' route
        assert response.status_code == 200
        assert b"Question ID:" in response.data

        # Assert new exam and questions exist in the database
        new_exam = Exam.query.filter_by(user_id=ham_user.id, element='2').first()
        assert new_exam is not None
        assert ExamAnswer.query.filter_by(exam_id=new_exam.id).count() == 35

        # Navigate away from exam page
        response = client.get(url_for('main.profile'))
        assert response.status_code == 200

        # Navigate back to exam page
        response = client.get(url_for('main.take_exam', exam_id=new_exam.id))
        assert response.status_code == 200

        assert b"Question ID:" in response.data

def test_launch_exam_no_registration(client, app):
    """Test ID: UT-186
    Negative test to ensure an error is shown when there is no valid registration.

    This test checks that a user cannot start an exam session if they do not have
    a valid registration for the specified exam element.

    Args:
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - Test user can log in successfully.
        - Exam launch request without valid registration returns a 200 status code.
        - Response data contains an error message about invalid registration.
        - Response data contains a redirection to the sessions page.
    """
    with app.app_context():
        # Get the test user created by the fixture
        ham_user = User.query.filter_by(username="TESTUSER").first()

        # Log in as the test user
        response = login(client, ham_user.username, 'testpassword')
        assert response.status_code == 200

        # Send POST request to launch exam without a valid registration
        response = client.post(
            url_for('main.launch_exam'),
            data={
                'session_id': 1,
                'exam_element': '2'
            },
            follow_redirects=True
        )

        # Assert error message is flashed
        assert response.status_code == 200
        assert b"You are not registered for this exam session or your registration is invalid." \
            in response.data

        # Assert redirection to sessions page
        assert b"sessions" in response.data

def test_launch_exam_missing_input(client, app):
    """Test ID: UT-187
    Negative test to ensure error handling for missing input data.

    This test verifies that the user receives an error when required input
    data (session_id or exam_element) is missing from the exam launch request.

    Args:
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - Test user can log in successfully.
        - Exam launch request without required input returns a 200 status code.
        - Response data contains an error message about missing input.
        - Response data contains a redirection to the sessions page.
    """
    with app.app_context():
        # Get the test user created by the fixture
        ham_user = User.query.filter_by(username="TESTUSER").first()

        # Create pools for exam session
        tech_pool = Pool(name="Tech Pool",
                        element="2",
                        start_date=datetime.now(),
                        end_date=datetime.now())
        gen_pool = Pool(name="General Pool",
                        element="3",
                        start_date=datetime.now(),
                        end_date=datetime.now())
        extra_pool = Pool(name="Extra Pool",
                        element="4",
                        start_date=datetime.now(),
                        end_date=datetime.now())
        db.session.add(tech_pool)
        db.session.add(gen_pool)
        db.session.add(extra_pool)
        db.session.commit()
        tech_id = tech_pool.id
        gen_id = gen_pool.id
        extra_id = extra_pool.id

        # Create a valid exam registration and session
        exam_session = ExamSession(
            session_date=datetime.today(),
            tech_pool_id=tech_id,
            gen_pool_id=gen_id,
            extra_pool_id=extra_id
        )
        db.session.add(exam_session)
        db.session.commit()

        # Log in as the test user
        response = login(client, ham_user.username, 'testpassword')
        assert response.status_code == 200

        # Send POST request to launch exam without session_id or exam_element
        response = client.post(
            url_for('main.launch_exam'),
            data={},
            follow_redirects=True
        )

        # Assert error message is flashed
        assert response.status_code == 200
        assert b"Invalid exam request. Missing required information." in response.data

        # Assert redirection to sessions page
        assert b"Exam Sessions" in response.data

def test_launch_exam_role_not_allowed(client, ve_user):
    """Test ID: UT-188
    Negative test: Ensure that users with the VE role cannot access the launch exam page.

    Args:
        client: The test client instance.

    Asserts:
        - The response status code is 302 (redirect).
        - The response redirects to the logout page.
        - An 'Access denied' message is flashed.
    """
    login(client, ve_user.username, 'vepassword')

    response = client.post(
        url_for('main.launch_exam'),
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b'Access denied' in response.data

def test_launch_exam_invalid_tech_element(client, app):
    """Test ID: UT-189
    Negative test to ensure an error message is shown when a user tries to start 
    a Technician exam without a valid registration for that element.

    This test checks that the user cannot launch a Technician exam session if they 
    do not have a valid registration for it.

    Args:
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - Test user can log in successfully.
        - Exam launch request for Technician element returns a 200 status code.
        - Response data contains an error message about invalid registration for Technician exam.
    """
    with app.app_context():
        # Get the test user created by the fixture
        ham_user = User.query.filter_by(username="TESTUSER").first()

        # Create pools for exam session
        tech_pool = Pool(name="Tech Pool",
                        element="2",
                        start_date=datetime.now(),
                        end_date=datetime.now())
        gen_pool = Pool(name="General Pool",
                        element="3",
                        start_date=datetime.now(),
                        end_date=datetime.now())
        extra_pool = Pool(name="Extra Pool",
                        element="4",
                        start_date=datetime.now(),
                        end_date=datetime.now())
        db.session.add(tech_pool)
        db.session.add(gen_pool)
        db.session.add(extra_pool)
        db.session.commit()
        tech_id = tech_pool.id
        gen_id = gen_pool.id
        extra_id = extra_pool.id

        # Create a valid exam registration and session
        exam_session = ExamSession(
            session_date=datetime.today(),
            tech_pool_id=tech_id,
            gen_pool_id=gen_id,
            extra_pool_id=extra_id
        )
        db.session.add(exam_session)
        db.session.commit()

        exam_registration = ExamRegistration(
            user_id=ham_user.id,
            session_id=exam_session.id,
            tech=False,
            gen=False,
            extra=False,
            valid=True
        )
        db.session.add(exam_registration)
        db.session.commit()

        # Log in as the test user
        response = login(client, ham_user.username, 'testpassword')
        assert response.status_code == 200

        # Send POST request to launch exam
        response = client.post(
            url_for('main.launch_exam'),
            data={
                'session_id': exam_session.id,
                'exam_element': '2',
                'exam_name': get_exam_name('2')
            },
            follow_redirects=True
        )

        # Assert error message is flashed
        assert response.status_code == 200
        print(response.data)
        assert b"You are not registered for the Tech exam." in response.data

def test_launch_exam_invalid_general_element(client, app):
    """Test ID: UT-190
    Negative test to ensure an error message is shown when a user tries to start 
    a General exam without a valid registration for that element.

    This test checks that the user cannot launch a General exam session if they 
    do not have a valid registration for it.

    Args:
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - Test user can log in successfully.
        - Exam launch request for General element returns a 200 status code.
        - Response data contains an error message about invalid registration for General exam.
    """
    with app.app_context():
        # Get the test user created by the fixture
        ham_user = User.query.filter_by(username="TESTUSER").first()

        # Create pools for exam session
        tech_pool = Pool(name="Tech Pool",
                        element="2",
                        start_date=datetime.now(),
                        end_date=datetime.now())
        gen_pool = Pool(name="General Pool",
                        element="3",
                        start_date=datetime.now(),
                        end_date=datetime.now())
        extra_pool = Pool(name="Extra Pool",
                        element="4",
                        start_date=datetime.now(),
                        end_date=datetime.now())
        db.session.add(tech_pool)
        db.session.add(gen_pool)
        db.session.add(extra_pool)
        db.session.commit()
        tech_id = tech_pool.id
        gen_id = gen_pool.id
        extra_id = extra_pool.id

        # Create a valid exam registration and session
        exam_session = ExamSession(
            session_date=datetime.today(),
            tech_pool_id=tech_id,
            gen_pool_id=gen_id,
            extra_pool_id=extra_id
        )
        db.session.add(exam_session)
        db.session.commit()

        exam_registration = ExamRegistration(
            user_id=ham_user.id,
            session_id=exam_session.id,
            tech=True,
            gen=False,
            extra=False,
            valid=True
        )
        db.session.add(exam_registration)
        db.session.commit()

        # Log in as the test user
        response = login(client, ham_user.username, 'testpassword')
        assert response.status_code == 200

        # Send POST request to launch exam
        response = client.post(
            url_for('main.launch_exam'),
            data={
                'session_id': exam_session.id,
                'exam_element': '3',
                'exam_name': get_exam_name('3')
            },
            follow_redirects=True
        )

        # Assert error message is flashed
        assert response.status_code == 200
        assert b"You are not registered for the General exam." in response.data

def test_launch_exam_invalid_extra_element(client, app):
    """Test ID: UT-191
    Negative test to ensure an error message is shown when a user tries to start 
    an Extra exam without a valid registration for that element.

    This test checks that the user cannot launch an Extra exam session if they 
    do not have a valid registration for it.

    Args:
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - Test user can log in successfully.
        - Exam launch request for Extra element returns a 200 status code.
        - Response data contains an error message about invalid registration for Extra exam.
    """
    with app.app_context():
        # Get the test user created by the fixture
        ham_user = User.query.filter_by(username="TESTUSER").first()

        # Create pools for exam session
        tech_pool = Pool(name="Tech Pool",
                        element="2",
                        start_date=datetime.now(),
                        end_date=datetime.now())
        gen_pool = Pool(name="General Pool",
                        element="3",
                        start_date=datetime.now(),
                        end_date=datetime.now())
        extra_pool = Pool(name="Extra Pool",
                        element="4",
                        start_date=datetime.now(),
                        end_date=datetime.now())
        db.session.add(tech_pool)
        db.session.add(gen_pool)
        db.session.add(extra_pool)
        db.session.commit()
        tech_id = tech_pool.id
        gen_id = gen_pool.id
        extra_id = extra_pool.id

        # Create a valid exam registration and session
        exam_session = ExamSession(
            session_date=datetime.today(),
            tech_pool_id=tech_id,
            gen_pool_id=gen_id,
            extra_pool_id=extra_id
        )
        db.session.add(exam_session)
        db.session.commit()

        exam_registration = ExamRegistration(
            user_id=ham_user.id,
            session_id=exam_session.id,
            tech=True,
            gen=False,
            extra=False,
            valid=True
        )
        db.session.add(exam_registration)
        db.session.commit()

        # Log in as the test user
        response = login(client, ham_user.username, 'testpassword')
        assert response.status_code == 200

        # Send POST request to launch exam
        response = client.post(
            url_for('main.launch_exam'),
            data={
                'session_id': exam_session.id,
                'exam_element': '4',
                'exam_name': get_exam_name('4')
            },
            follow_redirects=True
        )

        # Assert error message is flashed
        assert response.status_code == 200
        assert b"You are not registered for the Extra exam." in response.data

def test_launch_exam_sqlalchemy_error(client, app, ve_user):
    """Test ID: UT-192
    Unit test to ensure that the SQLAlchemyError is handled correctly 
    during the exam session creation process.

    This test simulates a database error during the exam creation step.

    Args:
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - Test user can log in successfully.
        - Simulated SQLAlchemyError is raised during the transaction.
        - Response data contains a flash message about the database error.
    """
    with app.app_context():
        # Get the test user created by the fixture
        ham_user = User.query.filter_by(username="TESTUSER").first()

        # Create pools for exam session
        tech_pool = Pool(name="Tech Pool",
                        element="2",
                        start_date=datetime.now(),
                        end_date=datetime.now())
        gen_pool = Pool(name="General Pool",
                        element="3",
                        start_date=datetime.now(),
                        end_date=datetime.now())
        extra_pool = Pool(name="Extra Pool",
                        element="4",
                        start_date=datetime.now(),
                        end_date=datetime.now())
        db.session.add(tech_pool)
        db.session.add(gen_pool)
        db.session.add(extra_pool)
        db.session.commit()
        tech_id = tech_pool.id
        gen_id = gen_pool.id
        extra_id = extra_pool.id

        # Prepare a CSV file-like object to upload
        csv_content = """id,correct,question,a,b,c,d,refs
T1A01,A,What is 1+1?,2,3,4,5,Reference1
T1B02,B,What is 2+2?,1,4,3,5,Reference2
T1C03,C,What is 3+3?,1,2,6,5,Reference3
T1D04,D,What is 4+4?,4,8,3,5,Reference4
T1E05,A,What is 5+5?,10,1,3,5,Reference5
T1F06,B,What is 6+6?,1,12,4,5,Reference6
T1G07,C,What is 7+7?,14,3,4,5,Reference7
T1H08,D,What is 8+8?,4,3,16,5,Reference8
T1I09,A,What is 9+9?,18,3,4,5,Reference9
T1J10,B,What is 10+10?,1,20,4,5,Reference10
T1K11,C,What is 11+11?,1,22,4,5,Reference11
T1L12,D,What is 12+12?,1,24,4,5,Reference12
T1M13,A,What is 13+13?,26,3,4,5,Reference13
T1N14,B,What is 14+14?,1,28,4,5,Reference14
T1O15,C,What is 15+15?,1,30,4,5,Reference15
T1P16,D,What is 16+16?,1,32,4,5,Reference16
T1Q17,A,What is 17+17?,34,3,4,5,Reference17
T1R18,B,What is 18+18?,1,36,4,5,Reference18
T1S19,C,What is 19+19?,1,38,4,5,Reference19
T1T20,D,What is 20+20?,1,40,4,5,Reference20
T1U21,A,What is 21+21?,42,3,4,5,Reference21
T1V22,B,What is 22+22?,1,44,4,5,Reference22
T1W23,C,What is 23+23?,1,46,4,5,Reference23
T1X24,D,What is 24+24?,1,48,4,5,Reference24
T1Y25,A,What is 25+25?,50,3,4,5,Reference25
T1Z26,B,What is 26+26?,1,52,4,5,Reference26
T2A27,C,What is 27+27?,1,54,4,5,Reference27
T2B28,D,What is 28+28?,1,56,4,5,Reference28
T2C29,A,What is 29+29?,58,3,4,5,Reference29
T2D30,B,What is 30+30?,1,60,4,5,Reference30
T2E31,C,What is 31+31?,1,62,4,5,Reference31
T2F32,D,What is 32+32?,1,64,4,5,Reference32
T2G33,A,What is 33+33?,66,3,4,5,Reference33
T2H34,B,What is 34+34?,1,68,4,5,Reference34
T2I35,C,What is 35+35?,1,70,4,5,Reference35
"""
        data = {
            'file': (BytesIO(csv_content.encode('utf-8')), 'questions.csv')
        }

        # Ensure a VE user is logged in
        login(client, ve_user.username, 'vepassword')

        response = client.post(f'/ve/upload_questions/{tech_id}',
                               data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        assert response.is_json
        assert response.get_json()['success'] is True

        # Logout ve_user
        logout(client)

        # Create a valid exam registration and session
        exam_session = ExamSession(
            session_date=datetime.today(),
            tech_pool_id=tech_id,
            gen_pool_id=gen_id,
            extra_pool_id=extra_id
        )
        db.session.add(exam_session)
        db.session.commit()

        exam_registration = ExamRegistration(
            user_id=ham_user.id,
            session_id=exam_session.id,
            tech=True,
            gen=False,
            extra=False,
            valid=True
        )
        db.session.add(exam_registration)
        db.session.commit()

        # Log in as the test user
        response = login(client, ham_user.username, 'testpassword')
        assert response.status_code == 200

        # Mock the database commit to raise SQLAlchemyError
        with patch('openwaves.db.session.commit', side_effect=SQLAlchemyError):
            response = client.post(
                url_for('main.launch_exam'),
                data={
                    'session_id': exam_session.id,
                    'exam_element': '2',
                    'exam_name': 'Technician'
                },
                follow_redirects=True
            )

            # Assert error message is flashed
            assert response.status_code == 200
            assert b"A database error occurred while creating the exam session." in response.data

def test_launch_exam_generic_exception(client, app, ve_user):
    """Test ID: UT-193
    Unit test to ensure that a generic exception is handled correctly 
    during the exam session creation process.

    This test simulates a generic exception during the transaction.

    Args:
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - Test user can log in successfully.
        - Simulated generic Exception is raised during the transaction.
        - Response data contains a flash message about an unexpected error.
    """
    with app.app_context():
        # Get the test user created by the fixture
        ham_user = User.query.filter_by(username="TESTUSER").first()

        # Create pools for exam session
        tech_pool = Pool(name="Tech Pool",
                        element="2",
                        start_date=datetime.now(),
                        end_date=datetime.now())
        gen_pool = Pool(name="General Pool",
                        element="3",
                        start_date=datetime.now(),
                        end_date=datetime.now())
        extra_pool = Pool(name="Extra Pool",
                        element="4",
                        start_date=datetime.now(),
                        end_date=datetime.now())
        db.session.add(tech_pool)
        db.session.add(gen_pool)
        db.session.add(extra_pool)
        db.session.commit()
        tech_id = tech_pool.id
        gen_id = gen_pool.id
        extra_id = extra_pool.id

        # Prepare a CSV file-like object to upload
        csv_content = """id,correct,question,a,b,c,d,refs
T1A01,A,What is 1+1?,2,3,4,5,Reference1
T1B02,B,What is 2+2?,1,4,3,5,Reference2
T1C03,C,What is 3+3?,1,2,6,5,Reference3
T1D04,D,What is 4+4?,4,8,3,5,Reference4
T1E05,A,What is 5+5?,10,1,3,5,Reference5
T1F06,B,What is 6+6?,1,12,4,5,Reference6
T1G07,C,What is 7+7?,14,3,4,5,Reference7
T1H08,D,What is 8+8?,4,3,16,5,Reference8
T1I09,A,What is 9+9?,18,3,4,5,Reference9
T1J10,B,What is 10+10?,1,20,4,5,Reference10
T1K11,C,What is 11+11?,1,22,4,5,Reference11
T1L12,D,What is 12+12?,1,24,4,5,Reference12
T1M13,A,What is 13+13?,26,3,4,5,Reference13
T1N14,B,What is 14+14?,1,28,4,5,Reference14
T1O15,C,What is 15+15?,1,30,4,5,Reference15
T1P16,D,What is 16+16?,1,32,4,5,Reference16
T1Q17,A,What is 17+17?,34,3,4,5,Reference17
T1R18,B,What is 18+18?,1,36,4,5,Reference18
T1S19,C,What is 19+19?,1,38,4,5,Reference19
T1T20,D,What is 20+20?,1,40,4,5,Reference20
T1U21,A,What is 21+21?,42,3,4,5,Reference21
T1V22,B,What is 22+22?,1,44,4,5,Reference22
T1W23,C,What is 23+23?,1,46,4,5,Reference23
T1X24,D,What is 24+24?,1,48,4,5,Reference24
T1Y25,A,What is 25+25?,50,3,4,5,Reference25
T1Z26,B,What is 26+26?,1,52,4,5,Reference26
T2A27,C,What is 27+27?,1,54,4,5,Reference27
T2B28,D,What is 28+28?,1,56,4,5,Reference28
T2C29,A,What is 29+29?,58,3,4,5,Reference29
T2D30,B,What is 30+30?,1,60,4,5,Reference30
T2E31,C,What is 31+31?,1,62,4,5,Reference31
T2F32,D,What is 32+32?,1,64,4,5,Reference32
T2G33,A,What is 33+33?,66,3,4,5,Reference33
T2H34,B,What is 34+34?,1,68,4,5,Reference34
T2I35,C,What is 35+35?,1,70,4,5,Reference35
"""
        data = {
            'file': (BytesIO(csv_content.encode('utf-8')), 'questions.csv')
        }

        # Ensure a VE user is logged in
        login(client, ve_user.username, 'vepassword')

        response = client.post(f'/ve/upload_questions/{tech_id}',
                               data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        assert response.is_json
        assert response.get_json()['success'] is True

        # Logout ve_user
        logout(client)

        # Create a valid exam registration and session
        exam_session = ExamSession(
            session_date=datetime.today(),
            tech_pool_id=tech_id,
            gen_pool_id=gen_id,
            extra_pool_id=extra_id
        )
        db.session.add(exam_session)
        db.session.commit()

        exam_registration = ExamRegistration(
            user_id=ham_user.id,
            session_id=exam_session.id,
            tech=True,
            gen=False,
            extra=False,
            valid=True
        )
        db.session.add(exam_registration)
        db.session.commit()

        # Log in as the test user
        response = login(client, ham_user.username, 'testpassword')
        assert response.status_code == 200

        # Mock the database commit to raise a generic Exception
        with patch('openwaves.db.session.commit', side_effect=Exception):
            response = client.post(
                url_for('main.launch_exam'),
                data={
                    'session_id': exam_session.id,
                    'exam_element': '2',
                    'exam_name': 'Technician'
                },
                follow_redirects=True
            )

            # Assert error message is flashed
            assert response.status_code == 200
            assert b"An unexpected error occurred. Please try again later." in response.data
