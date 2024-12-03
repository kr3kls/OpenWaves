"""File: test_take_exam.py

    This file contains the unit tests for the take_exam code in the main.py file.
"""

import pytest
from flask import url_for

@pytest.mark.usefixtures("app")
def test_take_exam_invalid_method(client):
    """Test ID: UT-62
    Test the take_exam route when an invalid method is used.

    This test ensures that only GET and POST methods are allowed.

    Asserts:
        - The response is a 405 Method Not Allowed error.
    """
    response = client.put(url_for('main.take_exam', exam_id=1), follow_redirects=True)

    assert response.status_code == 405
