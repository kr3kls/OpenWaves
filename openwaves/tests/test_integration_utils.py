"""File: test_utils.py

    This file contains the integration tests for the code in the utils.py file.
"""
from unittest.mock import patch, MagicMock
import pytest
from openwaves import db
from openwaves.models import User, Question
from openwaves.utils import update_user_password, generate_exam

def test_update_user_password(app):
    """Test ID: IT-38
    Test the update_user_password utility function.

    This test ensures that the user's password is successfully updated in the database
    when using the update_user_password function.

    Args:
        app: The Flask application instance.
        client: The test client instance.

    Asserts:
        - The user's password hash in the database is changed after the update.
    """
    with app.app_context():
        # Retrieve the existing test user
        user = User.query.filter_by(username="TESTUSER").first()
        original_password_hash = user.password # Store the original hash

        # Call the function to update the password
        new_password = "new_test_password"
        update_user_password(user, new_password)

        # flush database cache
        db.session.flush()

        # Retrieve the user again to check if the password has been updated
        updated_user = User.query.filter_by(username="TESTUSER").first()

        # Assert that the password has changed
        assert updated_user.password != original_password_hash  # Hashes should be different

@pytest.mark.usefixtures("app")
def test_generate_exam_success():
    """Test ID: IT-39
    Positive test: Verify successful generation of an exam with the required number of questions.

    Asserts:
        - The function returns a non-None exam object.
        - The exam contains the expected number of questions based on the pool element.
    """
    pool_id = 1
    pool = MagicMock(id=pool_id, element=2)
    tli_codes = ["ABC", "DEF", "GHI", "JKL", "MNO", "PQR", "STU", "VWX", "YZA", "BCD", "EFG",
                 "HIJ", "KLM", "NOP", "QRS", "TUV", "WXY", "ZAB", "CDE", "FGH", "IJK", "LMN",
                 "OPQ", "RST", "UVW", "XYZ", "BCD", "EFG", "HIJ", "KLM", "NOP", "QRS", "TUV",
                 "WXY", "ZAB"]

    # Mock TLI and Question objects
    tlis = [MagicMock(id=i, pool_id=pool_id, tli=code, quantity=5) \
            for i, code in enumerate(tli_codes, start=1)]
    questions = []
    for i, code in enumerate(tli_codes, start=1):
        for j in range(5):
            question = MagicMock(spec_set=Question)
            question.id = i
            question.pool_id = pool_id
            question.number = f"{code}{str(j+1).zfill(2)}"
            question.correct_answer = 1
            question.question = f"Sample question for {code}"
            question.option_a = "Option A"
            question.option_b = "Option B"
            question.option_c = "Option C"
            question.option_d = "Option D"
            question.refs = "Sample reference"
            questions.append(question)

    with patch("openwaves.db.session.get", return_value=pool):
        with patch("openwaves.models.TLI.query") as mock_tli_query:
            mock_tli_query.filter_by.return_value.all.return_value = tlis
            with patch("openwaves.models.Question.query") as mock_filter_question:
                mock_filter_question.filter_by.return_value.all.return_value = questions

                exam = generate_exam(pool_id)
                assert exam is not None
                assert len(exam) == 35
