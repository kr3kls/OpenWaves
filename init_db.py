# This script initializes the database

from project import db, create_app

# Create the app
app = create_app()

# Create the database within the app context
with app.app_context():
    db.create_all()
