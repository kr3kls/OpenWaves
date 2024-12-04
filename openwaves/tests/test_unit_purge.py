"""File: test_purge.py

    This file contains the unit tests for the purge sessions code in the main_ve.py file.
"""
from unittest.mock import patch
import pytest
from flask import url_for
from sqlalchemy.exc import SQLAlchemyError
from openwaves.tests.test_unit_auth import login

@pytest.mark.usefixtures("app")
def test_purge_sessions_database_error(client, ve_user):
    """Test ID: UT-69
    Negative test: Verify proper handling of SQLAlchemy error during purge.

    Asserts:
        - The response status code is 500.
        - The response JSON indicates an error.
    """
    # Log in as VE user (role 2)
    response = login(client, ve_user.username, 'vepassword')
    assert response.status_code == 200

    # Mock the delete operation to raise an SQLAlchemyError
    with patch('openwaves.db.session.query', side_effect=SQLAlchemyError("Database error")):
        response = client.delete(url_for('main_ve.purge_sessions'))

    # Validate response
    assert response.status_code == 500
    assert response.json.get("success") is False
    assert response.json.get("error") == "Database operation failed"
