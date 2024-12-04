"""File: test_init.py

    This file contains the integration tests for the code in the init.py file.
"""

import pytest
from werkzeug.security import generate_password_hash
from openwaves import db
from openwaves.models import User
from openwaves import load_user

def test_load_user_valid_id(app):
    """Test ID: IT-01
    Test that load_user returns the correct user for a valid user_id. This test ensures that the
    application loads users correctly.

    Args:
        app: The Flask application instance.

    Asserts:
        - The user is loaded.
        - The user id of the loaded user matches the desired user.
        - The username of the loaded user is 'testloaduser'.
    """
    with app.app_context():
        # Create a test user
        user = User(
            username='testloaduser',
            first_name='Test',
            last_name='User',
            email='testloaduser@example.com',
            password=generate_password_hash('password', method='pbkdf2:sha256'),
            role=1
        )
        db.session.add(user)
        db.session.commit()

        user_id = user.id

        # Now test load_user
        loaded_user = load_user(user_id)
        assert loaded_user is not None
        assert loaded_user.id == user.id
        assert loaded_user.username == 'testloaduser'

def test_load_user_invalid_id(app):
    """Test ID: IT-02
    Test that load_user returns None for an invalid user_id. This test ensures that the application
    does not load a user when it shouldn't.

    Args:
        app: The Flask application instance.

    Asserts:
        - The user is not loaded.
    """
    with app.app_context():
        invalid_user_id = 99999  # Assuming this ID doesn't exist

        # Now test load_user
        loaded_user = load_user(invalid_user_id)
        assert loaded_user is None

def test_load_user_non_integer_id(app):
    """Test ID: IT-03
    Test that load_user handles non-integer user_id gracefully. This test ensures that the
    application can handle erroneous data in place of userid.

    Args:
        app: The Flask application instance.

    Asserts:
        - The application raises a ValueError.
    """
    with app.app_context():
        non_integer_user_id = 'abc'

        # Now test load_user
        with pytest.raises(ValueError):
            _loaded_user = load_user(non_integer_user_id)
