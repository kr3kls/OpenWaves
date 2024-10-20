"""File: conftest.py

    This file contains the base configuration for application testing using pytest and tox.
"""

import os
import sys
import pytest
from werkzeug.security import generate_password_hash
from openwaves import create_app, db
from openwaves.models import User

# Add the project root directory to sys.path (this ensures Python can find openwaves)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def app():
    """Create and configure a new Flask application instance for each test.

    This fixture sets up the Flask app with testing configurations, initializes the database,
    and creates a test user. It yields the app instance for use in tests and cleans up the
    database after each test is done.
    """

    # Set up the Flask app with test configurations
    app = create_app({ # pylint: disable=W0621
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///test_db.sqlite",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test_secret_key"
    })

    # Set the correct root path and template folder for testing
    app.root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app.jinja_loader.searchpath = [os.path.join(app.root_path, 'templates')]

    # Push the app context before the test
    ctx = app.app_context()
    ctx.push()

    with app.app_context():
        db.create_all()

        # Create a test user
        test_user = User(
            username="TESTUSER",
            first_name="first_test",
            last_name="last_test",
            email="testuser@example.com",
            password=generate_password_hash("testpassword", method="pbkdf2:sha256"),
            role=1
        )
        db.session.add(test_user)
        db.session.commit()

    yield app

    db.session.remove()
    db.drop_all()
    ctx.pop()

@pytest.fixture
def client(app): # pylint: disable=W0621
    """Provide a test client for the Flask application.

    This fixture returns a Flask test client that can be used to simulate HTTP requests to the app
    without running a server.
    """
    return app.test_client()

@pytest.fixture
def runner(app): # pylint: disable=W0621
    """Provide a CLI runner for the Flask application.

    This fixture returns a Click runner that can invoke commands registered with the Flask app's 
    CLI.
    """
    return app.test_cli_runner()

@pytest.fixture
def ve_user(): # pylint: disable=W0621
    """Create a VE user with role=2 for testing."""

    new_ve_user = User(
        username="TESTVEUSER",
        first_name="VE",
        last_name="User",
        email="veuser@example.com",
        password=generate_password_hash("vepassword", method="pbkdf2:sha256"),
        role=2,
        active=True
    )
    db.session.add(new_ve_user)
    db.session.commit()
    return db.session.get(User, new_ve_user.id)

@pytest.fixture
def user_to_toggle(): # pylint: disable=W0621
    """Create a user whose status can be toggled and password reset."""

    user = User(
        username="USERTOTOGGLE",
        first_name="User",
        last_name="ToToggle",
        email="usertotoggle@example.com",
        password=generate_password_hash("password", method="pbkdf2:sha256"),
        role=1,
        active=True
    )
    db.session.add(user)
    db.session.commit()
    return db.session.get(User, user.id)
