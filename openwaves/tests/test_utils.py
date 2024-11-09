"""File: test_utils.py

    This file contains the tests for the code in the utils.py file.
"""
from unittest.mock import patch, MagicMock
import pytest
from openwaves import db
from openwaves.models import User, ExamRegistration, ExamDiagram, Question
from openwaves.utils import update_user_password, get_exam_name, is_already_registered, \
    remove_exam_registration, requires_diagram, get_exam_score, generate_exam

class MockExamAnswer: # pylint: disable=R0903
    """Mock class for simulating ExamAnswer objects in unit tests.

    This class is designed to create mock instances of ExamAnswer objects
    to be used in unit testing. It allows for easy instantiation of objects 
    with attributes that simulate actual ExamAnswer records from the database.

    Attributes:
        answer (int): The user's selected answer for the exam question.
        correct_answer (int): The correct answer for the exam question.
    """
    def __init__(self, answer, correct_answer):
        self.answer = answer
        self.correct_answer = correct_answer

def test_update_user_password(app):
    """Test ID: UT-30
    Test the update_user_password utility function.

    This test ensures that the user's password is successfully updated in the database
    when using the update_user_password function.

    Args:
        app: The Flask application instance.
        client: The test client instance.

    Asserts:
        - The user's password hash in the database is changed after the update.
    """
    with app.app_context():
        # Retrieve the existing test user
        user = User.query.filter_by(username="TESTUSER").first()
        original_password_hash = user.password # Store the original hash

        # Call the function to update the password
        new_password = "new_test_password"
        update_user_password(user, new_password)

        # flush database cache
        db.session.flush()

        # Retrieve the user again to check if the password has been updated
        updated_user = User.query.filter_by(username="TESTUSER").first()

        # Assert that the password has changed
        assert updated_user.password != original_password_hash  # Hashes should be different

def test_get_exam_name():
    """Test ID: UT-88
    Test the get_exam_name helper function.

    This test ensures that the function correctly maps exam element numbers to exam names,
    and returns an empty string for invalid inputs.

    Asserts:
        - The correct exam name is returned for valid exam element numbers ('2', '3', '4').
        - An empty string is returned for invalid or unexpected exam element numbers.
    """
    # Valid exam elements
    assert get_exam_name('2') == 'Tech'
    assert get_exam_name('3') == 'General'
    assert get_exam_name('4') == 'Extra'

    # Invalid exam elements
    assert get_exam_name('1') == ''
    assert get_exam_name('5') == ''
    assert get_exam_name('') == ''
    assert get_exam_name(None) == ''
    assert get_exam_name('abc') == ''

def test_is_already_registered():
    """Test ID: UT-89
    Test the is_already_registered helper function.

    This test ensures that the function correctly determines whether a user is already registered
    for a specific exam element based on their existing registration.

    Asserts:
        - Returns True if the user is registered for the given exam element.
        - Returns False if the user is not registered for the given exam element.
        - Handles cases where the existing registration is None or exam element is invalid.
    """
    # Create a mock ExamRegistration object
    registration = ExamRegistration(session_id='1',
                                    user_id='1',
                                    tech=True,
                                    gen=False,
                                    extra=False
                                    )

    # User is registered for Tech
    assert is_already_registered(registration, '2') is True
    # User is not registered for General
    assert is_already_registered(registration, '3') is False
    # User is not registered for Extra
    assert is_already_registered(registration, '4') is False

    # Update registration to include General
    registration.gen = True
    assert is_already_registered(registration, '3') is True

    # Update registration to include Extra
    registration.extra = True
    assert is_already_registered(registration, '4') is True

    # Invalid exam element
    assert is_already_registered(registration, '1') is False
    assert is_already_registered(registration, '') is False
    assert is_already_registered(registration, None) is False

    # Existing registration is None
    assert is_already_registered(None, '2') is False

def test_remove_exam_registration():
    """Test ID: UT-90
    Test the remove_exam_registration helper function.

    This test ensures that the function correctly updates the user's registration by setting
    the specified exam element's registration status to False.

    Asserts:
        - The specified exam element's registration is set to False.
        - Other exam elements remain unchanged.
        - Handles cases where the exam element is invalid or not registered.
    """
    # Create a mock ExamRegistration object with all elements registered
    registration = ExamRegistration(tech=True, gen=True, extra=True)

    # Remove Tech registration
    remove_exam_registration(registration, '2')
    assert registration.tech is False
    assert registration.gen is True
    assert registration.extra is True

    # Remove General registration
    remove_exam_registration(registration, '3')
    assert registration.tech is False
    assert registration.gen is False
    assert registration.extra is True

    # Remove Extra registration
    remove_exam_registration(registration, '4')
    assert registration.tech is False
    assert registration.gen is False
    assert registration.extra is False

    # Attempt to remove an exam element not registered (should have no effect)
    remove_exam_registration(registration, '2')
    assert registration.tech is False

    # Invalid exam element (should have no effect)
    remove_exam_registration(registration, '1')
    assert registration.tech is False
    assert registration.gen is False
    assert registration.extra is False

def test_remove_exam_registration_none_registration():
    """Test ID: UT-106
    Negative test: Verify that the function handles None for the existing_registration argument.

    Asserts:
        - The function does not raise an exception when existing_registration is None.
        - No changes are made since the input is invalid.
    """
    # Attempt to remove registration when existing_registration is None
    remove_exam_registration(None, '2')

def test_remove_exam_registration_none_exam_element():
    """Test ID: UT-107
    Negative test: Verify that the function handles None for the exam_element argument.

    Asserts:
        - The function does not raise an exception when exam_element is None.
        - No changes are made to the existing registration since the input is invalid.
    """
    # Create a mock ExamRegistration object with all elements registered
    registration = ExamRegistration(tech=True, gen=True, extra=True)

    # Attempt to remove registration with None as the exam_element
    remove_exam_registration(registration, None)
    assert registration.tech is True
    assert registration.gen is True
    assert registration.extra is True

def test_remove_exam_registration_none_both():
    """Test ID: UT-108
    Negative test: Verify that the function handles None for both arguments.

    Asserts:
        - The function does not raise an exception when both arguments are None.
    """
    # Attempt to remove registration when both arguments are None
    remove_exam_registration(None, None)

@pytest.mark.usefixtures("app")
def test_requires_diagram_matching_diagram():
    """Test ID: UT-196
    Test the requires_diagram function with a question that has a matching diagram.

    This test ensures that the function correctly identifies when a diagram is required
    for a given question, based on matching diagram names.

    Asserts:
        - The function returns a diagram object if a matching diagram is found.
        - The diagram name matches the expected diagram in the question.
    """
    question = type('Question', (), {})()
    question.pool_id = 1
    question.question = "Refer to diagram D-1"

    # Mock the filter_by method on the ExamDiagram query
    with patch('openwaves.models.ExamDiagram.query') as mock_query:
        mock_filter_by = mock_query.filter_by.return_value
        mock_filter_by.all.return_value = \
            [ExamDiagram(pool_id=1, name="D-1", path="path/to/diagram.jpg")]

        result = requires_diagram(question)

        assert result is not None
        assert result.name == "D-1"

@pytest.mark.usefixtures("app")
def test_requires_diagram_no_matching_diagram():
    """Test ID: UT-197
    Test the requires_diagram function with a question that does not have a matching diagram.

    This test ensures that the function correctly returns None when a question does not 
    require a diagram, even if diagrams exist for the pool ID.

    Asserts:
        - The function returns None when no matching diagram is found.
    """
    question = type('Question', (), {})()
    question.pool_id = 1
    question.question = "No diagram needed"

    diagrams = [ExamDiagram(pool_id=1, name="D-1", path="path/to/diagram.jpg")]
    with patch('openwaves.utils.ExamDiagram.query.filter_by') as mock_query:
        mock_query.return_value.all.return_value = diagrams

        result = requires_diagram(question)
        assert result is None

@pytest.mark.usefixtures("app")
def test_requires_diagram_no_diagrams():
    """Test ID: UT-198
    Test the requires_diagram function when no diagrams are available for the given pool ID.

    This test checks if the function correctly handles cases where there are no diagrams 
    associated with the specified pool ID.

    Asserts:
        - The function returns None when no diagrams are found for the given pool ID.
    """
    question = type('Question', (), {})()
    question.pool_id = 1
    question.question = "Refer to diagram D-1"

    diagrams = []
    with patch('openwaves.utils.ExamDiagram.query.filter_by') as mock_query:
        mock_query.return_value.all.return_value = diagrams

        result = requires_diagram(question)
        assert result is None

@pytest.mark.usefixtures("app")
def test_requires_diagram_empty_question():
    """Test ID: UT-199
    Test the requires_diagram function with an empty question string.

    This test verifies that the function correctly returns None when the question string is 
    empty, even if diagrams exist for the pool ID.

    Asserts:
        - The function returns None when the question string is empty.
    """
    question = type('Question', (), {})()
    question.pool_id = 1
    question.question = ""

    diagrams = [ExamDiagram(pool_id=1, name="D-1", path="path/to/diagram.jpg")]
    with patch('openwaves.utils.ExamDiagram.query.filter_by') as mock_query:
        mock_query.return_value.all.return_value = diagrams

        result = requires_diagram(question)
        assert result is None

@pytest.mark.usefixtures("app")
def test_requires_diagram_none_question():
    """Test ID: UT-200
    Test the requires_diagram function with a None value for the question string.

    This test ensures that the function returns None when the question string is set to None,
    even if diagrams exist for the pool ID.

    Asserts:
        - The function returns None when the question string is None.
    """
    question = type('Question', (), {})()
    question.pool_id = 1
    question.question = None

    diagrams = [ExamDiagram(pool_id=1, name="D-1", path="path/to/diagram.jpg")]
    with patch('openwaves.utils.ExamDiagram.query.filter_by') as mock_query:
        mock_query.return_value.all.return_value = diagrams

        result = requires_diagram(question)
        assert result is None

def test_get_exam_score_pass_tech_exam():
    """Test ID: UT-201
    Test the get_exam_score function for a passing score on the Technician exam (element 2).

    This test checks that the function correctly calculates a passing score 
    when the score is 26 or higher out of 35.

    Asserts:
        - The score string includes 'Pass' when the score is 26 or higher.
    """
    exam_answers = [MockExamAnswer(answer=1, correct_answer=1) for _ in range(26)] + \
                   [MockExamAnswer(answer=0, correct_answer=1) for _ in range(9)]

    result = get_exam_score(exam_answers, 2)
    assert result == 'Score: 26/35 (Pass)'

def test_get_exam_score_fail_tech_exam():
    """Test ID: UT-202
    Test the get_exam_score function for a failing score on the Technician exam (element 2).

    This test checks that the function correctly calculates a failing score 
    when the score is below 26 out of 35.

    Asserts:
        - The score string includes 'Fail' when the score is below 26.
    """
    exam_answers = [MockExamAnswer(answer=1, correct_answer=1) for _ in range(25)] + \
                   [MockExamAnswer(answer=0, correct_answer=1) for _ in range(10)]

    result = get_exam_score(exam_answers, 2)
    assert result == 'Score: 25/35 (Fail)'

def test_get_exam_score_pass_general_exam():
    """Test ID: UT-203
    Test the get_exam_score function for a passing score on the General exam (element 3).

    This test checks that the function correctly calculates a passing score 
    when the score is 26 or higher out of 35.

    Asserts:
        - The score string includes 'Pass' when the score is 26 or higher.
    """
    exam_answers = [MockExamAnswer(answer=1, correct_answer=1) for _ in range(30)] + \
                   [MockExamAnswer(answer=0, correct_answer=1) for _ in range(5)]

    result = get_exam_score(exam_answers, 3)
    assert result == 'Score: 30/35 (Pass)'

def test_get_exam_score_fail_general_exam():
    """Test ID: UT-204
    Test the get_exam_score function for a failing score on the General exam (element 3).

    This test checks that the function correctly calculates a failing score 
    when the score is below 26 out of 35.

    Asserts:
        - The score string includes 'Fail' when the score is below 26.
    """
    exam_answers = [MockExamAnswer(answer=1, correct_answer=1) for _ in range(20)] + \
                   [MockExamAnswer(answer=0, correct_answer=1) for _ in range(15)]

    result = get_exam_score(exam_answers, 3)
    assert result == 'Score: 20/35 (Fail)'

def test_get_exam_score_pass_extra_exam():
    """Test ID: UT-205
    Test the get_exam_score function for a passing score on the Extra exam (element 4).

    This test checks that the function correctly calculates a passing score 
    when the score is 37 or higher out of 50.

    Asserts:
        - The score string includes 'Pass' when the score is 37 or higher.
    """
    exam_answers = [MockExamAnswer(answer=1, correct_answer=1) for _ in range(37)] + \
                   [MockExamAnswer(answer=0, correct_answer=1) for _ in range(13)]

    result = get_exam_score(exam_answers, 4)
    assert result == 'Score: 37/50 (Pass)'

def test_get_exam_score_fail_extra_exam():
    """Test ID: UT-206
    Test the get_exam_score function for a failing score on the Extra exam (element 4).

    This test checks that the function correctly calculates a failing score 
    when the score is below 37 out of 50.

    Asserts:
        - The score string includes 'Fail' when the score is below 37.
    """
    exam_answers = [MockExamAnswer(answer=1, correct_answer=1) for _ in range(36)] + \
                   [MockExamAnswer(answer=0, correct_answer=1) for _ in range(14)]

    result = get_exam_score(exam_answers, 4)
    assert result == 'Score: 36/50 (Fail)'

def test_get_exam_score_invalid_element():
    """Test ID: UT-207
    Test the get_exam_score function with an invalid exam element.

    This test checks that the function returns None when an invalid exam 
    element is provided.

    Asserts:
        - The score string indicates 'None' when the element is invalid.
    """
    exam_answers = [MockExamAnswer(answer=1, correct_answer=1) for _ in range(10)]

    result = get_exam_score(exam_answers, 1)
    assert result == 'Score: 10/None (Fail)'

def test_get_exam_score_no_answers():
    """Test ID: UT-208
    Test the get_exam_score function with an empty list of exam answers.

    This test checks that the function handles an empty list of exam answers 
    correctly and returns a score of 0.

    Asserts:
        - The score string indicates 0/35 or 0/50 based on the exam element.
    """
    result_tech = get_exam_score([], 2)
    result_general = get_exam_score([], 3)
    result_extra = get_exam_score([], 4)

    assert result_tech == 'Score: 0/35 (Fail)'
    assert result_general == 'Score: 0/35 (Fail)'
    assert result_extra == 'Score: 0/50 (Fail)'

@pytest.mark.usefixtures("app")
def test_generate_exam_success():
    """Test ID: UT-238
    Positive test: Verify successful generation of an exam with the required number of questions.

    Asserts:
        - The function returns a non-None exam object.
        - The exam contains the expected number of questions based on the pool element.
    """
    pool_id = 1
    pool = MagicMock(id=pool_id, element=2)
    tli_codes = ["ABC", "DEF", "GHI", "JKL", "MNO", "PQR", "STU", "VWX", "YZA", "BCD", "EFG",
                 "HIJ", "KLM", "NOP", "QRS", "TUV", "WXY", "ZAB", "CDE", "FGH", "IJK", "LMN",
                 "OPQ", "RST", "UVW", "XYZ", "BCD", "EFG", "HIJ", "KLM", "NOP", "QRS", "TUV",
                 "WXY", "ZAB"]

    # Mock TLI and Question objects
    tlis = [MagicMock(id=i, pool_id=pool_id, tli=code, quantity=5) \
            for i, code in enumerate(tli_codes, start=1)]
    questions = []
    for i, code in enumerate(tli_codes, start=1):
        for j in range(5):
            question = MagicMock(spec_set=Question)
            question.id = i
            question.pool_id = pool_id
            question.number = f"{code}{str(j+1).zfill(2)}"
            question.correct_answer = 1
            question.question = f"Sample question for {code}"
            question.option_a = "Option A"
            question.option_b = "Option B"
            question.option_c = "Option C"
            question.option_d = "Option D"
            question.refs = "Sample reference"
            questions.append(question)

    with patch("openwaves.db.session.get", return_value=pool):
        with patch("openwaves.models.TLI.query") as mock_tli_query:
            mock_tli_query.filter_by.return_value.all.return_value = tlis
            with patch("openwaves.models.Question.query") as mock_filter_question:
                mock_filter_question.filter_by.return_value.all.return_value = questions

                exam = generate_exam(pool_id)
                assert exam is not None
                assert len(exam) == 35

def test_generate_exam_no_pool():
    """Test ID: UT-239
    Negative test: Verify that the function handles a non-existent pool ID.

    Asserts:
        - The function returns None when the specified pool ID does not exist.
    """
    pool_id = 999
    with patch("openwaves.db.session.get", return_value=None):
        exam = generate_exam(pool_id)
        assert exam is None

@pytest.mark.usefixtures("app")
def test_generate_exam_no_tlis():
    """Test ID: UT-240
    Negative test: Verify that the function handles cases where no TLIs are associated with
    the pool.

    Asserts:
        - The function returns None when no TLIs are found for the given pool.
    """
    pool_id = 1
    pool = MagicMock(id=pool_id, element=3)
    with patch("openwaves.db.session.get", return_value=pool):
        with patch("openwaves.models.TLI.query") as mock_tli_query:
            mock_tli_query.filter_by.return_value.all.return_value = []

            exam = generate_exam(pool_id)
            assert exam is None

@pytest.mark.usefixtures("app")
def test_generate_exam_no_questions_for_tlis():
    """Test ID: UT-241
    Negative test: Verify that the function handles cases where there are no questions for the
    TLIs in the pool.

    Asserts:
        - The function returns None when there are TLIs, but no associated questions.
    """
    pool_id = 1
    pool = MagicMock(id=pool_id, element=3)
    tli_codes = ["ABC", "DEF"]
    tlis = [MagicMock(tli=code) for code in tli_codes]

    with patch("openwaves.db.session.get", return_value=pool):
        with patch("openwaves.models.TLI.query") as mock_tli_query:
            with patch("openwaves.models.Question.query") as mock_filter_question:
                mock_tli_query.filter_by.return_value.all.return_value = tlis
                mock_filter_question.filter_by.return_value.all.return_value = []

                exam = generate_exam(pool_id)
                assert exam is None

@pytest.mark.usefixtures("app")
def test_generate_exam_incomplete_exam():
    """Test ID: UT-242
    Negative test: Verify that the function handles cases where there are insufficient questions
    to create a complete exam.

    Asserts:
        - The function returns None when there are fewer questions than required for the
          specified pool element.
    """
    pool_id = 1
    pool = MagicMock(id=pool_id, element=4)

    tlis = [MagicMock(id=1, pool_id=pool_id, tli="ABC", quantity=5)]
    questions = [MagicMock(spec_set=Question, number="ABC01")]

    with patch("openwaves.db.session.get", return_value=pool):
        with patch("openwaves.models.TLI.query") as mock_tli_query:
            with patch("openwaves.models.Question.query") as mock_filter_question:
                mock_tli_query.filter_by.return_value.all.return_value = tlis
                mock_filter_question.filter_by.return_value.all.return_value = questions

                exam = generate_exam(pool_id)
                assert exam is None

@pytest.mark.usefixtures("app")
def test_generate_exam_non_standard_element():
    """Test ID: UT-243
    Edge test: Verify that the function handles unsupported element types for the pool.

    Asserts:
        - The function returns None when the pool element is of an unsupported type.
    """
    pool_id = 1
    pool = MagicMock(id=pool_id, element=99)

    with patch("openwaves.db.session.get", return_value=pool):
        exam = generate_exam(pool_id)
        assert exam is None
