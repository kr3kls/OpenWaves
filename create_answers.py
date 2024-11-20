"""File: create_answers.py

   This script creates exam answers for exam sessions in the database. This is used to test the
   data analysis functionality of the application. The script creates exam answers for 100 exams.
"""
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from openwaves.models import ExamSession, Pool, ExamAnswer, Exam, User, ExamRegistration
from openwaves import create_app, db
from openwaves.utils import generate_exam

def main(): # pylint: disable=R0914
    """Main method to create exam answers for exam sessions."""

    # Initialize Flask app context
    app = create_app()

    with app.app_context():
        # Start a database session
        Session = sessionmaker(bind=db.engine) # pylint: disable=C0103
        session = Session()

        try:
            # Query all Pool and User records
            pools = session.query(Pool).all()
            users = session.query(User).filter(User.role == 1).all()

            # Ensure there are enough pools for each exam type
            if len(pools) < 3:
                raise ValueError("Not enough pools available for Technician, General, and Extra exams.") # pylint: disable=C0301

            tech_pool, gen_pool, extra_pool = pools[:3]

            # Create 10 exam sessions with random dates within the past year
            today = datetime.now()
            exam_sessions = []
            for _ in range(10):
                session_date = today - timedelta(days=random.randint(1, 365))
                start_time = session_date.replace(hour=random.randint(8, 12), minute=0, second=0)
                end_time = start_time + timedelta(hours=random.randint(1, 3))

                exam_session = ExamSession(
                    session_date=session_date,
                    start_time=start_time,
                    end_time=end_time,
                    tech_pool_id=tech_pool.id,
                    gen_pool_id=gen_pool.id,
                    extra_pool_id=extra_pool.id,
                    status=False
                )
                session.add(exam_session)
                exam_sessions.append(exam_session)

            # Save the exam sessions to the database
            session.commit()

            # Create one exam answer set per user per exam session
            for exam_session in exam_sessions:
                for user in users:
                    # Create a new exam registration
                    registration = ExamRegistration(
                        session_id=exam_session.id,
                        user_id=user.id,
                        tech=True,
                        gen=False,
                        extra=False,
                        valid=True
                    )
                    session.add(registration)
                    session.commit()

                    # Create a new exam
                    exam = Exam(
                        user_id=user.id,
                        pool_id=tech_pool.id,
                        session_id=exam_session.id,
                        element=tech_pool.element,
                        open=False
                    )

                    session.add(exam)
                    session.commit()

                    # Generate exam questions
                    exam_questions = generate_exam(tech_pool.id)

                    # Create exam answers
                    for question in exam_questions:
                        # Create an exam answer
                        exam_answer = ExamAnswer(
                            exam_id=exam.id,
                            question_id=question.id,
                            question_number=question.number,
                            answer=get_answer(question.correct_answer),
                            correct_answer=question.correct_answer
                        )
                        session.add(exam_answer)

            # Commit the changes to the database
            session.commit()
            print("Successfully created exam answers for all users and sessions.")

        except Exception as e:  # pylint: disable=W0718
            # Roll back any changes if an error occurs
            session.rollback()
            print(f"An error occurred: {e}")

        finally:
            # Close the session
            session.close()

def get_answer(correct_answer):
    """Return a random answer for a given correct answer."""
    random_float = random.random()

    if random_float > 0.76:
        # Generate a list of incorrect answers
        incorrect_answers = [option for option in [0, 1, 2, 3] if option != correct_answer]
        # Return a random incorrect answer
        return random.choice(incorrect_answers)

    return correct_answer

if __name__ == "__main__":
    main()
