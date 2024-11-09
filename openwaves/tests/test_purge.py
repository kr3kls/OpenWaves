"""File: test_purge.py

    This file contains the tests for the purge sessions code in the main_ve.py file.
"""
from datetime import datetime, timedelta
from unittest.mock import patch
import pytest
from flask import url_for
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError
from openwaves import db
from openwaves.imports import ExamSession, Pool
from openwaves.tests.test_auth import login

@pytest.mark.usefixtures("app")
def test_purge_sessions_authorized_success(client, ve_user):
    """Test ID: UT-263
    Functional test: Verify successful purge for sessions older than 15 months.
    
    Asserts:
        - The response status code is 200.
        - The response JSON indicates success.
    """
    # Set up a mock pool, required for the foreign key constraints
    pool = Pool(
        name="Tech Pool",
        element=2,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    db.session.add(pool)
    db.session.commit()

    # Set up mock data for a session older than 15 months
    old_date = datetime.now() - timedelta(days=460)
    old_session = ExamSession(
        session_date=old_date,
        tech_pool_id=pool.id,
        gen_pool_id=pool.id,
        extra_pool_id=pool.id,
        status=False
    )
    db.session.add(old_session)
    db.session.commit()

    # Log in as authorized VE user (role 2)
    response = login(client, ve_user.username, 'vepassword')
    assert response.status_code == 200

    # Simulate a DELETE request to purge sessions
    response = client.delete(url_for('main_ve.purge_sessions'))

    # Validate response
    assert response.status_code == 200
    assert response.json.get("success") is True

    # Check that the session has been deleted
    try:
        deleted_session = db.session.query(ExamSession).filter_by(id=old_session.id).one()
    except sqlalchemy.orm.exc.ObjectDeletedError:
        deleted_session = None

    # Assert that the session is indeed deleted
    assert deleted_session is None

@pytest.mark.usefixtures("app")
def test_purge_sessions_unauthorized_role(client, user_to_toggle):
    """Test ID: UT-264
    Negative test: Verify access denial for non-VE user (role != 2).

    Asserts:
        - The response redirects to the logout page.
        - An access denied flash message is present.
    """
    # Log in as a user without VE privileges (role not equal to 2)
    response = login(client, user_to_toggle.username, 'password')
    assert response.status_code == 200

    # Attempt to send a DELETE request to purge sessions
    response = client.delete(url_for('main_ve.purge_sessions'), follow_redirects=True)

    # Validate response
    assert response.status_code == 200
    assert b"Access denied." in response.data

@pytest.mark.usefixtures("app")
def test_purge_sessions_database_error(client, ve_user):
    """Test ID: UT-265
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

@pytest.mark.usefixtures("app")
def test_purge_sessions_no_old_sessions(client, ve_user):
    """Test ID: UT-266
    Functional test: Verify purge operation when no sessions are older than 15 months.

    Asserts:
        - The response status code is 200.
        - The response JSON indicates success.
    """
    # Set up a mock pool, required for foreign key constraints in ExamSession
    pool = Pool(
        name="Tech Pool",
        element=2,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    db.session.add(pool)
    db.session.commit()

    # Set up a session within the last 15 months with all required fields
    recent_date = datetime.now() - timedelta(days=300)
    recent_session = ExamSession(
        session_date=recent_date,
        tech_pool_id=pool.id,
        gen_pool_id=pool.id,
        extra_pool_id=pool.id,
        status=False
    )
    db.session.add(recent_session)
    db.session.commit()

    # Log in as VE user (role 2)
    response = login(client, ve_user.username, 'vepassword')
    assert response.status_code == 200

    # Simulate a DELETE request to purge sessions
    response = client.delete(url_for('main_ve.purge_sessions'))

    # Validate response
    assert response.status_code == 200
    assert response.json.get("success") is True
