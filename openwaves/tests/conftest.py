import pytest
import os
import sys
from openwaves import create_app, db
from openwaves.models import User
from werkzeug.security import generate_password_hash

# Add the project root directory to sys.path (this ensures Python can find openwaves)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def app():
    # Set the correct root directory to openwaves/ (the application root)
    app = create_app()

    # Set the correct root path and template folder for testing
    app.root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Force Flask to use the correct template folder (this might be redundant but ensures no issues)
    app.jinja_loader.searchpath = [os.path.join(app.root_path, 'templates')]

    # Print debugging info for the root path and template search paths
    # print(f"App root path: {app.root_path}") TODO Delete this when troubleshooting is complete
    # print(f"Template search paths: {app.jinja_loader.searchpath}") TODO Delete this when troubleshooting is complete

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
            username="testuser",
            first_name="first_test",
            last_name="last_test",
            email="testuser@example.com",
            password=generate_password_hash("testpassword", method="pbkdf2:sha256"),
            role=1
        )
        db.session.add(test_user)
        db.session.commit()

    yield app

    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
