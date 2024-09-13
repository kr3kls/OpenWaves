from openwaves.models import User
from werkzeug.security import generate_password_hash
from openwaves import db

def login(client, username, password):
    return client.post('/auth/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)

def test_get_login(client):
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b"OpenWaves Login" in response.data 

def test_login_post_valid(client):
    response = login(client, 'testuser', 'testpassword')
    assert response.status_code == 200
    # Since 'testuser' has role=1, should redirect to 'main.profile'
    assert b"Profile" in response.data

def test_login_post_valid_ve(client, app):
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
    response = login(client, 'testuser', 'wrongpassword')
    assert response.status_code == 200
    assert b"Please check your login details and try again." in response.data

def test_login_post_nonexistent_user(client):
    response = login(client, 'nonexistentuser', 'somepassword')
    assert response.status_code == 200
    assert b"Please check your login details and try again." in response.data

def test_get_signup(client):
    response = client.get('/auth/signup')
    assert response.status_code == 200
    assert b"FCC FRN" in response.data

def test_signup_post_valid(client, app):
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

def test_ve_signup_post_valid(client, app):
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

def test_logout(client):
    # Log in as 'testuser'
    login(client, 'testuser', 'testpassword')
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been logged out." in response.data
    # Verify that the user is logged out
    with client.session_transaction() as session:
        assert 'user_id' not in session
