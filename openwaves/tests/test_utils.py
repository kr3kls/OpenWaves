"""File: test_utils.py

    This file contains the tests for the code in the utils.py file.
"""
import pytest
from unittest.mock import patch
from openwaves import db
from openwaves.models import User, ExamRegistration, ExamDiagram
from openwaves.utils import update_user_password, get_exam_name, is_already_registered, \
    remove_exam_registration, requires_diagram

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
