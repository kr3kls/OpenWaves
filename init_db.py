"""File: init_db.py

    This script initializes the database.
"""
import random
from werkzeug.security import generate_password_hash
from openwaves import db, create_app
from openwaves.models import User

# Generate realistic first and last names
FIRST_NAMES = ["John",
               "Jane",
               "Michael",
               "Emily",
               "David",
               "Sarah",
               "Chris",
               "Amanda",
               "Brian",
               "Laura"]
LAST_NAMES = ["Smith",
              "Johnson",
              "Brown",
              "Taylor",
              "Anderson",
              "Thomas",
              "Jackson",
              "White",
              "Harris",
              "Martin"]

# Create the app
app = create_app()

# Create the database within the app context
with app.app_context():
    # Create the tables
    db.create_all()

    # Create 10 fake users
    for i in range(10):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        username = f"{first_name.lower()}{last_name.lower()}{i+1}"
        email = f"{first_name.lower()}.{last_name.lower()}{i+1}@example.com"
        password = generate_password_hash("Test@1234", method="pbkdf2:sha256")

        fake_user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            role=1
        )
        db.session.add(fake_user)

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
    db.session.add(ve_user)

    # Commit the changes
    db.session.commit()
