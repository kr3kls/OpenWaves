def test_login(client):
    # Attempt login with valid credentials
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "testpassword"
    }, follow_redirects=True)
    print(response.data)  # Debugging line
    assert response.status_code == 200

    # Attempt login with invalid credentials
    response = client.post("/auth/login", data={
        "username": "wronguser",
        "password": "wrongpassword"
    }, follow_redirects=True)
    print(response.data)  # Debugging line
    assert b"Please check your login details and try again." in response.data
