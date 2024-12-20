"""File: test_auth.py

    This file contains the integration tests for the code in the auth.py file.
"""

import re
from flask_login import current_user
from werkzeug.security import generate_password_hash, check_password_hash
from openwaves import db
from openwaves.models import User
from openwaves.tests.test_unit_auth import login, logout

#######################
#                     #
#     Login Tests     #
#                     #
#######################

def test_login_post_valid(client):
    """Test ID: IT-04
    Test logging in with valid credentials redirects to the profile page.
    """
    response = login(client, 'testuser', 'testpassword')
    assert response.status_code == 200
    # Since 'testuser' has role=1, should redirect to 'main.profile'
    assert b"OpenWaves Profile" in response.data

def test_login_post_valid_ve(client, app):
    """Test ID: IT-05
    Test that a VE user can log in and is redirected to the VE account page.

    Args:
        client: The test client.
        app: The Flask application instance.
    """
    # Create a VE user (role=2)
    with app.app_context():
        ve_user = User(
            username='VEUSER',
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
    # Should redirect to 'main.ve_profile'
    assert b"OpenWaves VE Profile" in response.data

def test_login_post_invalid_password(client):
    """Test ID: IT-06
    Test logging in with an invalid password shows an error message.
    """
    response = login(client, 'testuser', 'wrongpassword')
    assert response.status_code == 200
    assert b"Please check your login details and try again." in response.data

def test_login_post_nonexistent_user(client):
    """Test ID: IT-07
    Test logging in with a nonexistent username shows an error message.
    """
    response = login(client, 'nonexistentuser', 'somepassword')
    assert response.status_code == 200
    assert b"Please check your login details and try again." in response.data

########################
#                      #
#     Signup Tests     #
#                      #
########################

def test_signup_post_valid(client, app):
    """Test ID: IT-08
    Test that a new user can sign up successfully.

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

def test_signup_post_existing_username(client, app):
    """Test ID: IT-09
    Test that signing up with an existing username shows an error message.

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

###########################
#                         #
#     VE Signup Tests     #
#                         #
###########################

def test_ve_signup_post_valid(client, app):
    """Test ID: IT-10
    Test that a VE account can be created successfully.

    Args:
        client: The test client.
        app: The Flask application instance.
    """
    response = client.post('/auth/ve_signup', data={
        'username': 'newveuser',
        'first_name': 'New',
        'last_name': 'User',
        'email': 'newveuser@example.com',
        'password': 'newpassword',
        'confirm_password': 'newpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    # Should redirect to login page
    response = login(client, 'newveuser', 'newpassword')
    assert b"OpenWaves VE Profile" in response.data
    # Verify user creation
    with app.app_context():
        user = User.query.filter_by(username='NEWVEUSER').first()
        assert user is not None
        assert user.active is True

def test_ve_signup_post_valid_second(client, app):
    """Test ID: IT-11
    Test that a second VE account can be created successfully.

    Args:
        client: The test client.
        app: The Flask application instance.
    """
    response = client.post('/auth/ve_signup', data={
        'username': 'newveuser1',
        'first_name': 'New',
        'last_name': 'User',
        'email': 'newveuser@example.com',
        'password': 'newpassword',
        'confirm_password': 'newpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    # Should redirect to login page
    assert b"Login" in response.data
    # Verify user creation
    with app.app_context():
        user = User.query.filter_by(username='NEWVEUSER1').first()
        assert user is not None
        assert user.active is True # First account should be active

    response = client.post('/auth/ve_signup', data={
        'username': 'newveuser2',
        'first_name': 'New',
        'last_name': 'User',
        'email': 'newveuser@example.com',
        'password': 'newpassword',
        'confirm_password': 'newpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    # Should redirect to login page
    assert b"Login" in response.data
    # Verify user creation
    with app.app_context():
        user = User.query.filter_by(username='NEWVEUSER2').first()
        assert user is not None
        assert user.active is False # Second account should be disabled

def test_ve_signup_existing_username(client, app):
    """Test ID: IT-12
    Test that VE signup with an existing username shows an error message.

    Args:
        client: The test client.
        app: The Flask application instance.
    """
    # Create an existing user
    with app.app_context():
        existing_user = User(
            username='VEUSER3',
            first_name='VE',
            last_name='User',
            email='veuser3@example.com',
            password=generate_password_hash('somepassword', method='pbkdf2:sha256'),
            role=2
        )
        db.session.add(existing_user)
        db.session.commit()

    response = client.post('/auth/ve_signup', data={
        'username': 'veuser3',
        'first_name': 'New',
        'last_name': 'User',
        'email': 'newveuser@example.com',
        'password': 'vepassword',
        'confirm_password': 'vepassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Error 42, Please contact the Lead VE." in response.data

################################
#                              #
#     Update Profile Tests     #
#                              #
################################

def test_update_profile_success(client, app):
    """Test ID: IT-13
    Test updating the user profile successfully.

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

    # Update profile with valid data (user role=1)
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

def test_update_ve_profile_success(client, app):
    """Test ID: IT-14
    Test updating the user profile successfully.

    This test logs in as 'testveuser' and updates the profile with valid data,
    including changing the password.

    Args:
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - Response status code is 200.
        - Response data contains 'Profile updated successfully!'.
        - User data in the database is updated accordingly.
    """
    # Create a VE user
    response = client.post('/auth/ve_signup', data={
        'username': 'testveuser',
        'first_name': 'New',
        'last_name': 'User',
        'email': 'newveuser@example.com',
        'password': 'testvepassword',
        'confirm_password': 'testvepassword'
    }, follow_redirects=True)
    assert response.status_code == 200

    # Log in as testuser
    login(client, 'testveuser', 'testvepassword')

    # Update profile with valid data (user role=2)
    response = client.post('/auth/update_profile', data={
        'username': 'updatedveuser',
        'first_name': 'Updatedve',
        'last_name': 'Userve',
        'email': 'updatedve@example.com',
        'password': 'newvepassword',
        'confirm_password': 'newvepassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Profile updated successfully!' in response.data

    # Verify that the user's data has been updated
    with app.app_context():
        user = User.query.filter_by(username='updatedveuser').first()
        assert user is not None
        assert user.first_name == 'Updatedve'
        assert user.last_name == 'Userve'
        assert user.email == 'updatedve@example.com'
        # Verify password change
        assert check_password_hash(user.password, 'newvepassword')

def test_update_profile_invalid_role(client, app):
    """Test ID: IT-15
    Test updating the user profile with an invalid user role.

    This test logs in as 'testuser' and changes the current_user role to 3. 
    It then attempts to update the profile.

    Args:
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - Response status code is 200.
        - Response data contains 'You have been logged out.'.
        - User data in the database is not updated.
    """
    # Log in as testuser
    login(client, 'testuser', 'testpassword')

    # Change the current_user role to invalid number (3)
    current_user.role = 3

    # Update profile with valid data (user role=1)
    response = client.post('/auth/update_profile', data={
        'username': 'testuser',
        'first_name': 'Updated',
        'last_name': 'User',
        'email': 'updated@example.com',
        'password': 'newpassword',
        'confirm_password': 'newpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been logged out." in response.data

    # Verify that the user's data has not been updated
    with app.app_context():
        user = User.query.filter_by(username='TESTUSER').first()
        assert user is not None
        assert user.first_name == 'first_test'
        assert user.last_name == 'last_test'
        assert user.email == 'testuser@example.com'
        # Verify password did not change
        assert check_password_hash(user.password, 'testpassword')

def test_update_profile_no_password_change(client):
    """Test ID: IT-16
    Test updating the profile without changing the password.

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

###############################
#                             #
#     VE Management Tests     #
#                             #
###############################

def test_ve_management_access_as_ve_user(client, ve_user):
    """Test ID: IT-17
    Functional test: VE user can access VE management page.
    
    Args:
        client: The test client.
        ve_user: The VE user fixture.
    """
    login(client, ve_user.username, 'vepassword')
    response = client.get('/auth/ve_management')
    assert response.status_code == 200
    assert b'VE Account Management' in response.data

def test_ve_management_access_as_regular_user(client):
    """Test ID: IT-18
    Negative test: Regular user cannot access VE management page.
    
    Args:
        client: The test client.
    """
    login(client, 'TESTUSER', 'testpassword')
    response = client.get('/auth/ve_management', follow_redirects=True)
    assert b'Access denied.' in response.data

################################
#                              #
#     Account Status Tests     #
#                              #
################################

def test_toggle_account_status_as_ve_user(client, ve_user, user_to_toggle):
    """Test ID: IT-19
    Functional test: VE user can toggle account status.
    
    Args:
        client: The test client.
        ve_user: The VE user fixture.
        user_to_toggle: The user fixture whose status will be toggled.
    """
    login(client, ve_user.username, 'vepassword')
    with client.application.app_context():
        user = db.session.get(User, user_to_toggle.id)
        original_status = user.active
    response = client.post(f'/auth/toggle_account_status/{user_to_toggle.id}',
                           follow_redirects=True)
    expected_status = 'active' if not original_status else 'disabled'
    assert f'Account status updated to {expected_status}.' in response.get_data(as_text=True)
    with client.application.app_context():
        updated_user = db.session.get(User, user_to_toggle.id)
        assert updated_user.active == (not original_status)

def test_toggle_account_status_as_regular_user(client, user_to_toggle):
    """Test ID: IT-20
    Negative test: Regular user cannot toggle account status.
    
    Args:
        client: The test client.
        user_to_toggle: The user fixture whose status will be toggled.
    """
    login(client, 'TESTUSER', 'testpassword')
    response = client.post(f'/auth/toggle_account_status/{user_to_toggle.id}',
                           follow_redirects=True)
    assert b'Access denied.' in response.data

def test_toggle_account_status_nonexistent_user(client, ve_user):
    """Test ID: IT-21
    Negative test: Toggling status of non-existent user.
    
    Args:
        client: The test client.
        user_to_toggle: The user fixture whose status will be toggled.
    """
    login(client, ve_user.username, 'vepassword')
    response = client.post('/auth/toggle_account_status/9999', follow_redirects=True)
    assert b'Account not found.' in response.data

################################
#                              #
#     Password Reset Tests     #
#                              #
################################

def test_password_resets_access_as_ve_user(client, ve_user):
    """Test ID: IT-22
    Functional test: VE user can access password resets page.
    
     Args:
        client: The test client.
        ve_user: The VE user fixture.
    """
    login(client, ve_user.username, 'vepassword')
    response = client.get('/auth/password_resets')
    assert response.status_code == 200
    assert b'Password Resets' in response.data

def test_password_resets_access_as_regular_user(client):
    """Test ID: IT-23
    Negative test: Regular user cannot access password resets page.
    
     Args:
        client: The test client.
    """
    login(client, 'TESTUSER', 'testpassword')
    response = client.get('/auth/password_resets', follow_redirects=True)
    assert b'Access denied.' in response.data

def test_reset_password_as_ve_user(client, ve_user, user_to_toggle):
    """Test ID: IT-24
    Functional test: VE user can reset a user's password.
    
     Args:
        client: The test client.
        ve_user: The VE user fixture.
        user_to_toggle: The user fixture whose password will be reset.
    """
    login(client, ve_user.username, 'vepassword')
    response = client.post(f'/auth/reset_password/{user_to_toggle.id}', follow_redirects=True)
    data = response.get_data(as_text=True)
    assert f'Password for {user_to_toggle.username} has been reset.' in data
    # Extract the new password from the flash message
    match = re.search(r'New password: (\w+)', data)
    assert match is not None
    new_password = match.group(1)
    # Log out VE user
    logout(client)
    # Log in as the user with the new password
    response = login(client, user_to_toggle.username, new_password)
    assert b'OpenWaves Profile' in response.data

def test_reset_password_as_regular_user(client, user_to_toggle):
    """Test ID: IT-25
    Negative test: Regular user cannot reset another user's password.
    
    Args:
        client: The test client.
        user_to_toggle: The user fixture whose status will be toggled.
    """
    login(client, 'TESTUSER', 'testpassword')
    response = client.post(f'/auth/reset_password/{user_to_toggle.id}', follow_redirects=True)
    assert b'Access denied.' in response.data

def test_reset_password_nonexistent_user(client, ve_user):
    """Test ID: IT-26
    Negative test: Resetting password of non-existent user.
    
    Args:
        client: The test client.
        ve_user: The VE user fixture.
    """
    login(client, ve_user.username, 'vepassword')
    response = client.post('/auth/reset_password/9999', follow_redirects=True)
    assert b'Account not found.' in response.data
