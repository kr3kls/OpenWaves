"""File: init_ol_db.py

    This script takes the existing exam sessions and makes them 2 years older. This is used to test
    the purge functionality.
"""
from sqlalchemy.orm import sessionmaker
from openwaves.models import ExamSession
from openwaves import create_app, db

# Initialize Flask app context
app = create_app()

with app.app_context():
    # Start a database session
    Session = sessionmaker(bind=db.engine)
    session = Session()

    try:
        # Query all ExamSession records
        exam_sessions = session.query(ExamSession).all()

        # Update each session_date to be two years earlier
        for exam_session in exam_sessions:
            if exam_session.session_date:
                exam_session.session_date = \
                    exam_session.session_date.replace(year=exam_session.session_date.year - 2)

        # Commit the changes to the database
        session.commit()
        print("Successfully updated exam session dates to be two years earlier.")

    except Exception as e:
        # Roll back any changes if an error occurs
        session.rollback()
        print(f"An error occurred: {e}")

    finally:
        # Close the session
        session.close()
