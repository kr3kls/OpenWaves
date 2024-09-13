from openwaves.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from openwaves import db
from openwaves.tests.test_auth import login

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome to OpenWaves" in response.data

def test_profile_access(client):
    # Access profile without logging in
    response = client.get('/profile', follow_redirects=True)
    assert response.status_code == 200
    assert b"OpenWaves Login" in response.data  # Should redirect to login page

    # Log in and access profile
    response = login(client, 'testuser', 'testpassword')
    assert response.status_code == 200
    response = client.get('/profile')
    assert response.status_code == 200
    assert b"OpenWaves Profile" in response.data

def test_update_profile_success(client, app):
    # Log in as testuser
    login(client, 'testuser', 'testpassword')

    # Update profile with valid data
    response = client.post('/update_profile', data={
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
    # Log in as testuser
    login(client, 'testuser', 'testpassword')

    # Attempt to update profile with mismatched passwords
    response = client.post('/update_profile', data={
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
    # Log in as testuser
    login(client, 'testuser', 'testpassword')

    # Update profile without changing password
    response = client.post('/update_profile', data={
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

def test_ve_account_exists(client, app):
    # Create a VE account for testuser
    with app.app_context():
        ve_user = User(
            username='ve_testuser',
            first_name='Test',
            last_name='User',
            email='testuser@example.com',  # Same email as current_user
            password=generate_password_hash('vepassword', method='pbkdf2:sha256'),
            role=2
        )
        db.session.add(ve_user)
        db.session.commit()

    # Log in as testuser
    login(client, 'testuser', 'testpassword')

    # Access ve_account
    response = client.get('/ve_account')
    assert response.status_code == 200
    assert b"OpenWaves VE Account" in response.data

def test_ve_account_not_exists(client):
    # Log in as testuser
    login(client, 'testuser', 'testpassword')

    # Access ve_account when VE account doesn't exist
    response = client.get('/ve_account', follow_redirects=True)
    assert response.status_code == 200
    assert b"VE Account Signup" in response.data  # Should redirect to ve_signup page

def test_update_ve_account_success(client, app):
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
    response = client.post('/update_ve_account', data={
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
    # Log in as testuser
    login(client, 'testuser', 'testpassword')

    # Attempt to update VE account when it doesn't exist
    response = client.post('/update_ve_account', data={
        'username': 'updated_ve_user',
        'password': 'newvepassword',
        'confirm_password': 'newvepassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'VE account not found.' in response.data

def test_update_ve_account_password_mismatch(client, app):
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
    response = client.post('/update_ve_account', data={
        'username': 've_testuser',
        'password': 'newvepassword',
        'confirm_password': 'wrongpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    # check if the password remains unchanged
    with app.app_context():
        ve_user = User.query.filter_by(username='ve_testuser', role=2).first()
        assert check_password_hash(ve_user.password, 'vepassword')

def test_csp_violation_report_valid_json(client, capsys):
    violation_data = {
        "csp-report": {
            "document-uri": "http://example.com",
            "violated-directive": "script-src 'self'",
            "original-policy": "default-src 'none'; script-src 'self';",
            "blocked-uri": "http://evil.com/script.js"
        }
    }
    response = client.post('/csp-violation-report-endpoint', json=violation_data)
    assert response.status_code == 204

    # Capture the print output
    captured = capsys.readouterr()
    assert "CSP Violation:" in captured.out

def test_csp_violation_report_non_json(client, capsys):
    response = client.post('/csp-violation-report-endpoint', data='non-json data')
    assert response.status_code == 204

    # Capture the print output
    captured = capsys.readouterr()
    assert "Received non-JSON CSP violation report" in captured.out
