"""File: test_utils.py

    This file contains the tests for the code in the utils.py file.
"""

from openwaves import db
from openwaves.models import User
from openwaves.utils import update_user_password

def test_update_user_password(app):
    """Test the update_user_password utility function.

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
