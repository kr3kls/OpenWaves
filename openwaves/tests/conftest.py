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

    # Set the correct root directory to openwaves/ (the application root)
    app = create_app() # pylint: disable=W0621

    # Set the correct root path and template folder for testing
    app.root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Force Flask to use the correct template folder (this might be redundant but ensures no issues)
    app.jinja_loader.searchpath = [os.path.join(app.root_path, 'templates')]

    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # In-memory database for testing
        "SECRET_KEY": "test_secret_key"
    })

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
        test_ve_user = User(
            username="TESTVEUSER",
            first_name="first_test",
            last_name="last_test",
            email="testveuser@example.com",
            password=generate_password_hash("testvepassword", method="pbkdf2:sha256"),
            role=2
        )
        db.session.add(test_ve_user)
        db.session.commit()

    yield app

    with app.app_context():
        db.drop_all()

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
