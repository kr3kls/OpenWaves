from unittest.mock import patch
from flask import g

def test_login(client):
    # Mock the g.csp_nonce to return a static value
    with patch('secrets.token_hex', return_value='mocked_nonce'):
        
        # Attempt login with valid credentials
        response = client.post("/auth/login", data={
            "username": "testuser",
            "password": "testpassword"
        }, follow_redirects=True)
        
        print(response.data)  # Debugging line
        assert response.status_code == 200
        #assert "nonce=mocked_nonce" in response.headers.get("Content-Security-Policy", "")

        # Attempt login with invalid credentials
        response = client.post("/auth/login", data={
            "username": "wronguser",
            "password": "wrongpassword"
        }, follow_redirects=True)
        
        print(response.data)  # Debugging line
        assert b"Please check your login details and try again." in response.data
        #assert "nonce=mocked_nonce" in response.headers.get("Content-Security-Policy", "")