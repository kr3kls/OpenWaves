"""File: init_db.py

    This script initializes the database.
"""

from werkzeug.security import generate_password_hash
from openwaves import db, create_app
from openwaves.models import User

# Create the app
app = create_app()

# Create the database within the app context
with app.app_context():
    # Create the tables
    db.create_all()

    # Create a test user
    test_user = User(
        username="TESTUSER1",
        first_name="first_test",
        last_name="last_test",
        email="testuser@example.com",
        password=generate_password_hash("testpass1", method="pbkdf2:sha256"),
        role=1
    )
    db.session.add(test_user)

    # Create a VE user
    ve_user = User(
        username="N3GW",
        first_name="Craig",
        last_name="Troop",
        email="cdb34@psu.edu",
        password=generate_password_hash("testpass1", method="pbkdf2:sha256"),
        role=2
    )
    db.session.add(test_user)
    db.session.add(ve_user)
    db.session.commit()
