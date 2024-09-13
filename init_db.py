# This script initializes the database

from openwaves import db, create_app
from werkzeug.security import generate_password_hash
from openwaves.models import User

# Create the app
app = create_app()

# Create the database within the app context
with app.app_context():
    db.create_all()

     #Create a test user
    test_user = User(
        username="testuser1",
        first_name="first_test",
        last_name="last_test",
        email="testuser@example.com",
        password=generate_password_hash("testpass1", method="pbkdf2:sha256"),
        role=1
    )
    db.session.add(test_user)
    db.session.commit()
