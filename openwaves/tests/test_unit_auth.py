"""File: test_auth.py

    This file contains the tests for the code in the auth.py file.
"""

from werkzeug.security import check_password_hash
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

def logout(client):
    """Helper function to log out the current user."""
    return client.get('/auth/logout', follow_redirects=True)

#######################
#                     #
#     Login Tests     #
#                     #
#######################

def test_login_get(client):
    """Test ID: UT-01
    Test that the login page loads correctly.
    """
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b"OpenWaves Login" in response.data

########################
#                      #
#     Signup Tests     #
#                      #
########################

def test_signup_get(client):
    """Test ID: UT-02
    Test that the signup page loads correctly.
    """
    response = client.get('/auth/signup')
    assert response.status_code == 200
    assert b"FCC FRN" in response.data

def test_signup_post_password_mismatch(client):
    """Test ID: UT-03
    Test that signing up with mismatched passwords shows an error message.
    """
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

###########################
#                         #
#     VE Signup Tests     #
#                         #
###########################

def test_ve_signup_get(client):
    """Test ID: UT-04
    Test that the ve signup page loads correctly.

    Args:
        client: The test client.
    """
    response = client.get('/auth/ve_signup')
    assert response.status_code == 200
    assert b"Callsign" in response.data

def test_ve_signup_password_mismatch(client):
    """Test ID: UT-05
    Test that VE signup with mismatched passwords shows an error message.
    """
    response = client.post('/auth/ve_signup', data={
        'username': 'veuser2',
        'first_name': 'New',
        'last_name': 'User',
        'email': 'newveuser@example.com',
        'password': 'password1',
        'confirm_password': 'password2'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Passwords do not match" in response.data

################################
#                              #
#     Update Profile Tests     #
#                              #
################################

def test_update_profile_password_mismatch(client):
    """Test ID: UT-06
    Test updating the profile with mismatched passwords.

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

def test_logout(client):
    """Test ID: UT-07
    Test that a logged-in user can log out successfully.
    """
    # Log in as 'testuser'
    login(client, 'testuser', 'testpassword')
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been logged out." in response.data
    # Verify that the user is logged out
    with client.session_transaction() as session:
        assert 'user_id' not in session

###############################
#                             #
#     VE Management Tests     #
#                             #
###############################

def test_ve_management_access_not_logged_in(client):
    """Test ID: UT-08
    Negative test: Unauthenticated user cannot access VE management page.
    
    Args:
        client: The test client.
    """
    response = client.get('/auth/ve_management', follow_redirects=True)
    assert b'Please log in to access this page.' in response.data

################################
#                              #
#     Account Status Tests     #
#                              #
################################

def test_toggle_account_status_not_logged_in(client, user_to_toggle):
    """Test ID: UT-09
    Negative test: Unauthenticated user cannot toggle account status.
    
    Args:
        client: The test client.
        user_to_toggle: The user fixture whose status will be toggled.
    """
    response = client.post(f'/auth/toggle_account_status/{user_to_toggle.id}',
                           follow_redirects=True)
    assert b'Please log in to access this page.' in response.data

################################
#                              #
#     Password Reset Tests     #
#                              #
################################

def test_password_resets_access_not_logged_in(client):
    """Test ID: UT-10
    Negative test: Unauthenticated user cannot access password resets page.
    
     Args:
        client: The test client.
    """
    response = client.get('/auth/password_resets', follow_redirects=True)
    assert b'Please log in to access this page.' in response.data

def test_reset_password_not_logged_in(client, user_to_toggle):
    """Test ID: UT-11
    Negative test: Unauthenticated user cannot reset passwords.
    
    Args:
        client: The test client.
        user_to_toggle: The user fixture whose status will be toggled.
    """
    response = client.post(f'/auth/reset_password/{user_to_toggle.id}', follow_redirects=True)
    assert b'Please log in to access this page.' in response.data
