"""File: test_auth.py

    This file contains the tests for the code in the auth.py file.
"""

from werkzeug.security import generate_password_hash, check_password_hash
from openwaves import db
from openwaves.models import User

def login(client, username, password):
    """Helper function to log in a user during testing.

    Args:
        client: The test client.
        username (str): The username to log in with.
        password (str): The password to log in with.

    Returns:
        Response: The response object from the login attempt.
    """
    return client.post('/auth/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)

def test_get_login(client):
    """Test that the login page loads correctly."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b"OpenWaves Login" in response.data

def test_login_post_valid(client):
    """Test logging in with valid credentials redirects to the profile page."""
    response = login(client, 'testuser', 'testpassword')
    assert response.status_code == 200
    # Since 'testuser' has role=1, should redirect to 'main.profile'
    assert b"Profile" in response.data

def test_login_post_valid_ve(client, app):
    """Test that a VE user can log in and is redirected to the VE account page.

    Args:
        client: The test client.
        app: The Flask application instance.
    """
    # Create a VE user (role=2)
    with app.app_context():
        ve_user = User(
            username='veuser',
            first_name='VE',
            last_name='User',
            email='veuser@example.com',
            password=generate_password_hash('vepassword', method='pbkdf2:sha256'),
            role=2
        )
        db.session.add(ve_user)
        db.session.commit()
    response = login(client, 'veuser', 'vepassword')
    assert response.status_code == 200
    # Should redirect to 'main.ve_account'
    assert b"VE Account" in response.data

def test_login_post_invalid_password(client):
    """Test logging in with an invalid password shows an error message."""
    response = login(client, 'testuser', 'wrongpassword')
    assert response.status_code == 200
    assert b"Please check your login details and try again." in response.data

def test_login_post_nonexistent_user(client):
    """Test logging in with a nonexistent username shows an error message."""
    response = login(client, 'nonexistentuser', 'somepassword')
    assert response.status_code == 200
    assert b"Please check your login details and try again." in response.data

def test_get_signup(client):
    """Test that the signup page loads correctly."""
    response = client.get('/auth/signup')
    assert response.status_code == 200
    assert b"FCC FRN" in response.data

def test_signup_post_valid(client, app):
    """Test that a new user can sign up successfully.

    Args:
        client: The test client.
        app: The Flask application instance.
    """
    response = client.post('/auth/signup', data={
        'username': 'newuser',
        'first_name': 'New',
        'last_name': 'User',
        'email': 'newuser@example.com',
        'password': 'newpassword',
        'confirm_password': 'newpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    # Should redirect to login page
    assert b"Login" in response.data
    # Verify user creation
    with app.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None

def test_signup_post_password_mismatch(client):
    """Test that signing up with mismatched passwords shows an error message."""
    response = client.post('/auth/signup', data={
        'username': 'anotheruser',
        'first_name': 'Another',
        'last_name': 'User',
        'email': 'anotheruser@example.com',
        'password': 'password1',
        'confirm_password': 'password2'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Passwords do not match" in response.data

def test_signup_post_existing_username(client, app):
    """Test that signing up with an existing username shows an error message.

    Args:
        client: The test client.
        app: The Flask application instance.
    """
    # Create an existing user
    with app.app_context():
        existing_user = User(
            username='existinguser',
            first_name='Existing',
            last_name='User',
            email='existinguser@example.com',
            password=generate_password_hash('password', method='pbkdf2:sha256'),
            role=1
        )
        db.session.add(existing_user)
        db.session.commit()

    response = client.post('/auth/signup', data={
        'username': 'existinguser',  # Username already exists
        'first_name': 'Existing',
        'last_name': 'User',
        'email': 'existinguser@example.com',
        'password': 'password',
        'confirm_password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Error 42, Please contact a VE." in response.data

def test_update_profile_success(client, app):
    """Test updating the user profile successfully.

    This test logs in as 'testuser' and updates the profile with valid data,
    including changing the password.

    Args:
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - Response status code is 200.
        - Response data contains 'Profile updated successfully!'.
        - User data in the database is updated accordingly.
    """
    # Log in as testuser
    login(client, 'testuser', 'testpassword')

    # Update profile with valid data
    response = client.post('/auth/update_profile', data={
        'username': 'updateduser',
        'first_name': 'Updated',
        'last_name': 'User',
        'email': 'updated@example.com',
        'password': 'newpassword',
        'confirm_password': 'newpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Profile updated successfully!' in response.data

    # Verify that the user's data has been updated
    with app.app_context():
        user = User.query.filter_by(username='updateduser').first()
        assert user is not None
        assert user.first_name == 'Updated'
        assert user.last_name == 'User'
        assert user.email == 'updated@example.com'
        # Verify password change
        assert check_password_hash(user.password, 'newpassword')

def test_update_profile_password_mismatch(client):
    """Test updating the profile with mismatched passwords.

    This test ensures that when the new password and confirm password fields
    do not match, the profile is not updated, and the original password remains.

    Args:
        client: The test client instance.

    Asserts:
        - Response status code is 200.
        - User's password remains unchanged in the database.
    """
    # Log in as testuser
    login(client, 'testuser', 'testpassword')

    # Attempt to update profile with mismatched passwords
    response = client.post('/auth/update_profile', data={
        'username': 'testuser',
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'testuser@example.com',
        'password': 'newpassword',
        'confirm_password': 'wrongpassword'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Verify that the password remains unchanged
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        assert check_password_hash(user.password, 'testpassword')

def test_update_profile_no_password_change(client):
    """Test updating the profile without changing the password.

    This test verifies that when no new password is provided, the profile
    updates other fields, and the password remains unchanged.

    Args:
        client: The test client instance.

    Asserts:
        - Response status code is 200.
        - Response data contains 'Profile updated successfully!'.
        - User's other data is updated.
        - User's password remains unchanged.
    """
    # Log in as testuser
    login(client, 'testuser', 'testpassword')

    # Update profile without changing password
    response = client.post('/auth/update_profile', data={
        'username': 'testuser',
        'first_name': 'NewFirstName',
        'last_name': 'NewLastName',
        'email': 'newemail@example.com',
        'password': '',
        'confirm_password': ''
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Profile updated successfully!' in response.data

    # Verify that the user's data has been updated except the password
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        assert user.first_name == 'NewFirstName'
        assert user.last_name == 'NewLastName'
        assert user.email == 'newemail@example.com'
        # Verify password remains unchanged
        assert check_password_hash(user.password, 'testpassword')

def test_ve_signup_post_valid(client, app):
    """Test that a VE account can be created successfully.

    Args:
        client: The test client.
        app: The Flask application instance.
    """
    # First, log in as 'testuser'
    login(client, 'testuser', 'testpassword')
    response = client.post('/auth/ve_signup', data={
        'username': 'veuser',
        'password': 'vepassword',
        'confirm_password': 'vepassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    # Verify VE account creation
    with app.app_context():
        ve_user = User.query.filter_by(username='veuser').first()
        assert ve_user is not None
        assert ve_user.role == 2  # VE role
    assert b"VE account created successfully!" in response.data

def test_ve_signup_password_mismatch(client):
    """Test that VE signup with mismatched passwords shows an error message."""
    # Log in as 'testuser'
    login(client, 'testuser', 'testpassword')
    response = client.post('/auth/ve_signup', data={
        'username': 'veuser2',
        'password': 'password1',
        'confirm_password': 'password2'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Passwords do not match" in response.data

def test_ve_signup_existing_username(client, app):
    """Test that VE signup with an existing username shows an error message.

    Args:
        client: The test client.
        app: The Flask application instance.
    """
    # Create an existing user
    with app.app_context():
        existing_user = User(
            username='veuser3',
            first_name='VE',
            last_name='User',
            email='veuser3@example.com',
            password=generate_password_hash('somepassword', method='pbkdf2:sha256'),
            role=1
        )
        db.session.add(existing_user)
        db.session.commit()

    # Log in as 'testuser'
    login(client, 'testuser', 'testpassword')
    response = client.post('/auth/ve_signup', data={
        'username': 'veuser3',
        'password': 'vepassword',
        'confirm_password': 'vepassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Error 42, Please contact a VE." in response.data

def test_update_ve_account_success(client, app):
    """Test updating the VE account successfully.

    This test creates a VE account and then updates it with new credentials.

    Args:
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - Response status code is 200.
        - Response data contains 'VE account updated successfully!'.
        - VE user's data in the database is updated accordingly.
    """
    # Create a VE account for testuser
    with app.app_context():
        ve_user = User(
            username='ve_testuser',
            first_name='Test',
            last_name='User',
            email='testuser@example.com',
            password=generate_password_hash('vepassword', method='pbkdf2:sha256'),
            role=2
        )
        db.session.add(ve_user)
        db.session.commit()

    # Log in as testuser
    login(client, 'testuser', 'testpassword')

    # Update VE account with valid data
    response = client.post('/auth/update_ve_account', data={
        'username': 'updated_ve_user',
        'password': 'newvepassword',
        'confirm_password': 'newvepassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'VE account updated successfully!' in response.data

    # Verify VE account update
    with app.app_context():
        ve_user = User.query.filter_by(username='updated_ve_user', role=2).first()
        assert ve_user is not None
        assert check_password_hash(ve_user.password, 'newvepassword')

def test_update_ve_account_no_ve_account(client):
    """Test updating the VE account when it does not exist.

    This test attempts to update a VE account that hasn't been created,
    expecting an appropriate error message.

    Args:
        client: The test client instance.

    Asserts:
        - Response status code is 200.
        - Response data contains 'VE account not found.'.
    """
    # Log in as testuser
    login(client, 'testuser', 'testpassword')

    # Attempt to update VE account when it doesn't exist
    response = client.post('/auth/update_ve_account', data={
        'username': 'updated_ve_user',
        'password': 'newvepassword',
        'confirm_password': 'newvepassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'VE account not found.' in response.data

def test_update_ve_account_password_mismatch(client, app):
    """Test updating the VE account with mismatched passwords.

    This test ensures that when the new password and confirm password fields
    do not match during VE account update, the password remains unchanged.

    Args:
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - Response status code is 200.
        - VE user's password remains unchanged in the database.
    """
    # Create a VE account for testuser
    with app.app_context():
        ve_user = User(
            username='ve_testuser',
            first_name='Test',
            last_name='User',
            email='testuser@example.com',
            password=generate_password_hash('vepassword', method='pbkdf2:sha256'),
            role=2
        )
        db.session.add(ve_user)
        db.session.commit()

    # Log in as testuser
    login(client, 'testuser', 'testpassword')

    # Attempt to update VE account with mismatched passwords
    response = client.post('/auth/update_ve_account', data={
        'username': 've_testuser',
        'password': 'newvepassword',
        'confirm_password': 'wrongpassword'
    }, follow_redirects=True)
    assert response.status_code == 200

    # check if the password remains unchanged
    with app.app_context():
        ve_user = User.query.filter_by(username='ve_testuser', role=2).first()
        assert check_password_hash(ve_user.password, 'vepassword')

def test_logout(client):
    """Test that a logged-in user can log out successfully."""
    # Log in as 'testuser'
    login(client, 'testuser', 'testpassword')
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been logged out." in response.data
    # Verify that the user is logged out
    with client.session_transaction() as session:
        assert 'user_id' not in session
