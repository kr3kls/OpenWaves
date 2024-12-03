"""File: test_sessions.py

    This file contains the unit tests for the sessions code in the main.py file.
"""

#############################
#                           #
#     VE Sessions Tests     #
#                           #
#############################

def test_sessions_page_access_not_logged_in(client):
    """Test ID: UT-44
    Negative test: Ensures that unauthenticated users cannot access the sessions page.

    Args:
        client: The test client instance.

    Asserts:
        - The response data contains a message asking the user to log in.
        - The status code indicates a redirect to the login page.
    """
    response = client.get('/ve/sessions', follow_redirects=True)
    assert b'Please log in to access this page.' in response.data
