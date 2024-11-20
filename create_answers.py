"""File: create_answers.py

   This script creates exam answers for exam sessions in the database. This is used to test the
   data analysis functionality of the application. The script creates exam answers for 100 exams.
"""
import random
from sqlalchemy.orm import sessionmaker
from openwaves.models import ExamSession, Pool, ExamAnswer, Exam, User
from openwaves import create_app, db
from openwaves.utils import generate_exam

def main():
    """Main method to create exam answers for exam sessions."""

    # Initialize Flask app context
    app = create_app()

    with app.app_context():
        # Start a database session
        Session = sessionmaker(bind=db.engine)
        session = Session()

        try:
            # Query all ExamSession records
            exam_session = session.query(ExamSession).first()
            exam_pool = session.query(Pool).first()
            users = session.query(User).filter(User.role == 1).all()

            exam = Exam(
                user_id = random.choice(users).id,
                pool_id = exam_pool.id,
                session_id = exam_session.id,
                element = exam_pool.element,
                open = False
            )

            session.add(exam)
            session.commit()

            # Create exam answer data for 100 exam sessions
            for _ in range(1,100):
                # Generate an exam
                exam_questions = generate_exam(exam_pool.id)

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

                    # Add the exam answer to the session
                    session.add(exam_answer)

            # Commit the changes to the database
            session.commit()
            print("Successfully created exam answers.")

        except Exception as e: # pylint: disable=W0718
            # Roll back any changes if an error occurs
            session.rollback()
            print(f"An error occurred: {e}")

        finally:
            # Close the session
            session.close()

def get_answer(correct_answer):
    """Return a random answer for a given correct answer."""
    random_float = random.random()

    if random_float < 0.76:
        # Generate a list of incorrect answers
        incorrect_answers = [option for option in [0, 1, 2, 3] if option != correct_answer]
        # Return a random incorrect answer
        return random.choice(incorrect_answers)

    return correct_answer

if __name__ == "__main__":
    main()
