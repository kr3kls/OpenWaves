from openwaves.models import User
from openwaves.utils import update_user_password
from openwaves import db

def test_update_user_password(app, client):
    with app.app_context():
        # Retrieve the existing test user
        user = User.query.filter_by(username="testuser").first()
        original_password_hash = user.password # Store the original hash

        # Call the function to update the password
        new_password = "new_test_password"
        update_user_password(user, new_password)

        # flush database cache
        db.session.flush()

        # Retrieve the user again to check if the password has been updated
        updated_user = User.query.filter_by(username="testuser").first()
        
        # Assert that the password has changed
        assert updated_user.password != original_password_hash  # Hashes should be different
