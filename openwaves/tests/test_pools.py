"""File: test_pools.py

    This file contains the tests for the pools code in the main.py file.
"""
import os
from datetime import datetime
from io import BytesIO
from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError
from openwaves import db
from openwaves.imports import Pool, Question, TLI, ExamDiagram
from openwaves.tests.test_auth import login

def create_test_diagram(pool_id, path, session):
    """Helper function to create and add a diagram to the test database."""
    diagram = ExamDiagram(pool_id=pool_id, name="Test Diagram", path=path)
    session.add(diagram)
    session.commit()
    return diagram.id

def test_create_pool_success(client, ve_user):
    """Test ID: UT-49
    Functional test: Verifies that a VE user can successfully create a new question pool.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - The response status code is 200.
        - The response contains a JSON success message.
        - The newly created pool is present in the database with the correct element number.
    """
    login(client, ve_user.username, 'vepassword')
    response = client.post('/ve/create_pool', data={
        'pool_name': 'Test Pool',
        'exam_element': '2',
        'start_date': '2023-01-01',
        'end_date': '2026-12-31'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json()['success'] is True
    # Verify the pool was created in the database
    with client.application.app_context():
        pool = Pool.query.filter_by(name='Test Pool').first()
        assert pool is not None
        assert pool.element == 2

def test_create_pool_missing_fields(client, ve_user):
    """Test ID: UT-50
    Negative test: Verifies that creating a question pool with missing fields returns an error.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - The response status code is 400.
        - The response contains a JSON error message stating "All fields are required.".
    """
    login(client, ve_user.username, 'vepassword')
    response = client.post('/ve/create_pool', data={
        'pool_name': '',
        'exam_element': '',
        'start_date': '',
        'end_date': ''
    }, follow_redirects=True)
    assert response.status_code == 400
    assert response.is_json
    assert 'All fields are required.' in response.get_json()['error']

def test_upload_questions_success(client, ve_user):
    """Test ID: UT-53
    Functional test: Verifies that a VE user can successfully upload questions to a pool.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - The response status code is 200.
        - The response contains a JSON success message.
        - Two questions were added to the database, and one TLI entry was created.
    """
    # First, create a pool to upload questions to
    login(client, ve_user.username, 'vepassword')
    client.post('/ve/create_pool', data={
        'pool_name': 'Upload Test Pool',
        'exam_element': '2',
        'start_date': '2023-01-01',
        'end_date': '2026-12-31'
    }, follow_redirects=True)

    with client.application.app_context():
        pool = Pool.query.filter_by(name='Upload Test Pool').first()
        pool_id = pool.id

    # Prepare a CSV file-like object to upload
    csv_content = """id,correct,question,a,b,c,d,refs
T1A01,A,What is 1+1?,2,3,4,5,Reference1
T1A02,B,What is 2+2?,1,4,3,5,Reference2
"""
    data = {
        'file': (BytesIO(csv_content.encode('utf-8')), 'questions.csv')
    }

    response = client.post(f'/ve/upload_questions/{pool_id}',
                           data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json()['success'] is True

    # Verify that questions were added to the database
    with client.application.app_context():
        question_count = Question.query.filter_by(pool_id=pool_id).count()
        assert question_count == 2
        tli_count = TLI.query.filter_by(pool_id=pool_id).count()
        assert tli_count == 1  # Both questions have TLI starting with 'T1'

def test_upload_questions_no_file(client, ve_user):
    """Test ID: UT-54
    Negative test: Verifies that uploading questions without a file returns an error.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - The response status code is 400.
        - The response contains a JSON error message stating "No file provided.".
    """
    login(client, ve_user.username, 'vepassword')
    # Assume there's a pool with ID 1
    response = client.post('/ve/upload_questions/1', data={}, content_type='multipart/form-data')
    assert response.status_code == 400
    assert response.is_json
    assert 'No file provided.' in response.get_json()['error']

def test_upload_questions_invalid_file_type(client, ve_user):
    """Test ID: UT-55
    Negative test: Ensures that uploading a non-CSV file type returns an error.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - The response status code is 400.
        - The response contains an error message stating that only CSV files are allowed.
    """
    login(client, ve_user.username, 'vepassword')

    # Create a pool first
    client.post('/ve/create_pool', data={
        'pool_name': 'Invalid File Type Pool',
        'exam_element': '2',
        'start_date': '2023-01-01',
        'end_date': '2026-12-31'
    }, follow_redirects=True)

    with client.application.app_context():
        pool = Pool.query.filter_by(name='Invalid File Type Pool').first()
        pool_id = pool.id

    # Prepare a non-CSV file-like object to upload
    non_csv_content = "Not a CSV content"
    data = {
        'file': (BytesIO(non_csv_content.encode('utf-8')), 'questions.txt')
    }

    response = client.post(f'/ve/upload_questions/{pool_id}',
                           data=data, content_type='multipart/form-data')

    # Check for the appropriate error response
    assert response.status_code == 400
    assert b'Invalid file type. Only CSV files are allowed.' in response.data

def test_delete_pool_success(client, ve_user):
    """Test ID: UT-57
    Functional test: Verifies that a VE user can successfully delete a question pool.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - The response status code is 200, indicating successful pool deletion.
        - The response contains a JSON success message.
        - The pool is confirmed to have been deleted from the database.
    """
    login(client, ve_user.username, 'vepassword')
    # Create a pool to delete
    client.post('/ve/create_pool', data={
        'pool_name': 'Pool to Delete',
        'exam_element': '2',
        'start_date': '2023-01-01',
        'end_date': '2026-12-31'
    }, follow_redirects=True)
    with client.application.app_context():
        pool = Pool.query.filter_by(name='Pool to Delete').first()
        pool_id = pool.id

    response = client.delete(f'/ve/delete_pool/{pool_id}')
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json()['success'] is True
    # Verify the pool was deleted
    with client.application.app_context():
        pool = db.session.get(Pool, pool_id)
        assert pool is None

def test_delete_pool_not_found(client, ve_user):
    """Test ID: UT-58
    Negative test: Ensures that deleting a non-existent pool returns an error.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - The response status code is 404.
        - The response contains a JSON error message stating "Pool not found.".
    """
    login(client, ve_user.username, 'vepassword')
    response = client.delete('/ve/delete_pool/9999')
    assert response.status_code == 404
    assert response.is_json
    assert 'Pool not found.' in response.get_json()['error']

def test_upload_diagram_missing_file(client, app, ve_user):
    """Test ID: UT-165
    Test upload diagram with no file in request.

    This test ensures that when the file is missing in the request,
    an appropriate error message is flashed.

    Args:
        client: The test client instance.
        app: The Flask application instance.
        ve_user: The VE user fixture.

    Asserts:
        - The appropriate flash message is displayed when no file is provided.
        - The response redirects to the referring page.
    """
    # Ensure a VE user is logged in
    login(client, ve_user.username, 'vepassword')

    # Create a pool for testing
    with app.app_context():
        new_pool = Pool(name="Test Pool",
                        element="2",
                        start_date=datetime.now(),
                        end_date=datetime.now())
        db.session.add(new_pool)
        db.session.commit()
        pool_id = new_pool.id

    # Make a request without a file to the upload diagram route
    response = client.post(f'/ve/upload_diagram/{pool_id}', data={}, follow_redirects=True)

    # Assert the expected response
    assert response.status_code == 200
    assert b'No file part' in response.data

def test_upload_diagram_empty_filename(client, app, ve_user):
    """Test ID: UT-166
    Test upload diagram with an empty filename.

    This test ensures that when a file with an empty filename is provided,
    an appropriate error message is flashed.

    Args:
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - The appropriate flash message is displayed when the file has no name.
        - The response redirects to the referring page.
    """
    # Ensure a VE user is logged in
    login(client, ve_user.username, 'vepassword')

    data = {
        'file': (BytesIO(b'my file contents'), '')
    }
    with app.app_context():
        response = client.post('/ve/upload_diagram/1', data=data, follow_redirects=True)

        assert response.status_code == 200
        print(response.data)
        assert b'No selected file' in response.data

def test_upload_diagram_invalid_file_type(client, app, ve_user):
    """Test ID: UT-167
    Test upload diagram with an invalid file type.

    This test ensures that when an invalid file type is uploaded,
    an appropriate error message is flashed.

    Args:
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - The appropriate flash message is displayed for invalid file types.
        - The response redirects to the referring page.
    """
    # Ensure a VE user is logged in
    login(client, ve_user.username, 'vepassword')

    data = {
        'file': (BytesIO(b'my file contents'), 'test.txt')  # Invalid file type
    }
    with app.app_context():
        response = client.post('/ve/upload_diagram/1', data=data, follow_redirects=True)

        assert response.status_code == 200
        assert b'Invalid file type. Allowed types: png, jpg, jpeg, gif' in response.data

@patch('os.path.exists', return_value=False)
def test_upload_diagram_directory_does_not_exist(mock_exists, client, app, ve_user): # pylint: disable=W0613
    """Test ID: UT-168
    Test upload diagram when the directory does not exist.

    This test ensures that when the directory for storing uploads does not exist,
    an appropriate error message is flashed.

    Args:
        mock_exists: Mock for os.path.exists to simulate a non-existing directory.
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - The appropriate flash message is displayed when the directory doesn't exist.
        - The response redirects to the referring page.
    """
    # Ensure a VE user is logged in
    login(client, ve_user.username, 'vepassword')

    data = {
        'file': (BytesIO(b'my file contents'), 'test.png')
    }
    with app.app_context():
        response = client.post('/ve/upload_diagram/1', data=data, follow_redirects=True)

        assert response.status_code == 200
        assert b'Upload directory does not exist.' in response.data

@patch('os.path.exists', return_value=True)
@patch('werkzeug.datastructures.FileStorage.save')
def test_upload_diagram_successful(mock_save, mock_exists, client, app, ve_user): # pylint: disable=W0613
    """Test ID: UT-169
    Test successful upload of a diagram.

    This test ensures that when all conditions are met, the diagram is successfully uploaded,
    and the appropriate success message is flashed.

    Args:
        mock_save: Mock for FileStorage.save to simulate successful file saving.
        mock_exists: Mock for os.path.exists to simulate an existing directory.
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - The appropriate flash message is displayed for successful upload.
        - The response redirects to the pools page.
    """
    # Ensure a VE user is logged in
    login(client, ve_user.username, 'vepassword')

    data = {
        'file': (BytesIO(b'my file contents'), 'test.png'),
        'diagram_name': 'Test Diagram'
    }
    with app.app_context():
        response = client.post('/ve/upload_diagram/1', data=data, follow_redirects=True)

        assert response.status_code == 200
        assert b'Diagram uploaded successfully' in response.data

@patch('os.path.exists', return_value=True)
@patch('werkzeug.datastructures.FileStorage.save', side_effect=SQLAlchemyError)
def test_upload_diagram_database_error(mock_save, mock_exists, client, app, ve_user): # pylint: disable=W0613
    """Test ID: UT-170
    Test upload diagram with a database error.

    This test ensures that when there is a database error during the diagram save,
    an appropriate error message is flashed.

    Args:
        mock_save: Mock for FileStorage.save to simulate a database error.
        mock_exists: Mock for os.path.exists to simulate an existing directory.
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - The appropriate flash message is displayed for a database error.
        - The response redirects to the referring page.
    """
    # Ensure a VE user is logged in
    login(client, ve_user.username, 'vepassword')

    data = {
        'file': (BytesIO(b'my file contents'), 'test.png'),
        'diagram_name': 'Test Diagram'
    }
    with app.app_context():
        response = client.post('/ve/upload_diagram/1', data=data, follow_redirects=True)

        assert response.status_code == 200
        assert b'An error occurred while saving the diagram to the database.' in response.data

@patch('os.path.exists', return_value=True)
@patch('os.remove')
def test_delete_diagram_success(mock_remove, mock_exists, client, app, ve_user): # pylint: disable=W0613
    """Test ID: UT-172
    Test successful diagram deletion.

    This test ensures that when the diagram exists, it is successfully deleted from the server 
    and the database, and the appropriate success message is returned.

    Args:
        mock_remove: Mock for os.remove to simulate successful file removal.
        mock_exists: Mock for os.path.exists to simulate an existing file.
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - The diagram is deleted from the file system and the database.
        - A success message is returned.
    """
    # Ensure a VE user is logged in
    login(client, ve_user.username, 'vepassword')

    with app.app_context():
        # Create a test pool and diagram
        pool = Pool(name="Test Pool",
                    element="2",
                    start_date=datetime.now(),
                    end_date=datetime.now())
        db.session.add(pool)
        db.session.commit()

        exam_diagram = ExamDiagram(pool_id=pool.id, name="Test Diagram", path="diagrams/test.png")
        db.session.add(exam_diagram)
        db.session.commit()
        diagram_id = exam_diagram.id

    # Make the DELETE request to remove the diagram
    response = client.delete(f'/ve/delete_diagram/{diagram_id}', follow_redirects=True)

    # Assert successful removal
    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json == {"success": True}, f"Unexpected response: {response_json}"

    mock_remove.assert_called_once()

    # Verify the diagram was deleted from the database
    with app.app_context():
        diagram = db.session.get(ExamDiagram, diagram_id)
        assert diagram is None

def test_delete_diagram_not_found(client, ve_user):
    """Test ID: UT-173
    Test diagram deletion when diagram is not found.

    This test ensures that if the diagram does not exist, an appropriate error message is returned.

    Args:
        client: The test client instance.
        ve_user: The VE user fixture.

    Asserts:
        - The correct error message is returned when the diagram is not found.
        - The response status code is 404.
    """
    # Ensure a VE user is logged in
    login(client, ve_user.username, 'vepassword')

    # Attempt to delete a non-existent diagram
    response = client.delete('/ve/delete_diagram/9999', follow_redirects=True)

    # Assert the expected error response
    assert response.status_code == 404
    assert b'Diagram not found.' in response.data

@patch('os.path.exists', return_value=False)
def test_delete_diagram_file_not_found(mock_exists, client, app, ve_user): # pylint: disable=W0613
    """Test ID: UT-174
    Test diagram deletion when the diagram file does not exist on the server.

    This test ensures that when the diagram file is missing on the server, 
    an appropriate error message is returned.

    Args:
        mock_exists: Mock for os.path.exists to simulate a missing file.
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - The correct error message is returned when the file is not found.
        - The response status code is 404.
    """
    # Ensure a VE user is logged in
    login(client, ve_user.username, 'vepassword')

    with app.app_context():
        # Create a test pool and diagram in the database
        pool = Pool(name="Test Pool",
                    element="2",
                    start_date=datetime.now(),
                    end_date=datetime.now())
        db.session.add(pool)
        db.session.commit()

        exam_diagram = ExamDiagram(pool_id=pool.id, name="Test Diagram", path="diagrams/test.png")
        db.session.add(exam_diagram)
        db.session.commit()
        diagram_id = exam_diagram.id

    # Make the DELETE request with a missing file
    response = client.delete(f'/ve/delete_diagram/{diagram_id}', follow_redirects=True)

    # Assert the expected error response
    assert response.status_code == 404
    assert b'Diagram file not found.' in response.data

@patch('os.path.exists', return_value=True)
@patch('os.remove')
def test_delete_pool_diagram_file_exists(mock_remove, mock_exists, client, app, ve_user): # pylint: disable=W0613
    """Test ID: UT-179
    Test diagram deletion when the file exists on the server.

    This test ensures that when the diagram file exists on the server,
    it is successfully deleted from both the server and the database.

    Args:
        mock_remove: Mock for os.remove to simulate successful file removal.
        mock_exists: Mock for os.path.exists to simulate an existing file.
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - The diagram file is deleted from the server.
        - The diagram record is removed from the database.
        - The response status code is 200.
    """
    login(client, ve_user.username, 'vepassword')

    with app.app_context():
        # Create pool and diagram for testing
        pool = Pool(name="Test Pool", element="2",
                    start_date=datetime.now(),
                    end_date=datetime.now())
        db.session.add(pool)
        db.session.flush()

        diagram = ExamDiagram(pool_id=pool.id, name="Test Diagram", path="diagrams/test.png")
        db.session.add(diagram)
        db.session.flush()

        # DELETE request to remove the pool and diagrams
        response = client.delete(f'/ve/delete_pool/{pool.id}', follow_redirects=True)

    # Assert the request was successful
    assert response.status_code == 200

    # Verify the diagram file was removed
    mock_remove.assert_called_once_with(os.path.join(app.config['UPLOAD_FOLDER'], "test.png"))

    # Verify the diagram was deleted from the database
    with app.app_context():
        deleted_diagram = db.session.get(ExamDiagram, diagram.id)
        assert deleted_diagram is None

@patch('os.path.exists', return_value=False)
@patch('os.remove')
def test_delete_pool_diagram_file_not_found(mock_remove, mock_exists, client, app, ve_user): # pylint: disable=W0613
    """Test ID: UT-180
    Test diagram deletion when the file does not exist on the server.

    This test ensures that if the diagram file is missing on the server,
    the application logs an error and still deletes the diagram from the database.

    Args:
        mock_remove: Mock for os.remove to ensure it's not called.
        mock_exists: Mock for os.path.exists to simulate a missing file.
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - The diagram record is removed from the database.
        - The response status code is 200.
        - The os.remove function is not called.
    """
    login(client, ve_user.username, 'vepassword')

    with app.app_context():
        # Create a test pool and diagram
        pool = Pool(name="Test Pool", element="2",
                    start_date=datetime.now(),
                    end_date=datetime.now())
        db.session.add(pool)
        db.session.flush()

        diagram = ExamDiagram(pool_id=pool.id, name="Test Diagram", path="diagrams/missing.png")
        db.session.add(diagram)
        db.session.flush()

        # DELETE request to remove the pool
        response = client.delete(f'/ve/delete_pool/{pool.id}', follow_redirects=True)

    # Assert the request was successful
    assert response.status_code == 200

    # Ensure os.remove was not called
    mock_remove.assert_not_called()

    # Verify the diagram was deleted from the database
    with app.app_context():
        deleted_diagram = db.session.get(ExamDiagram, diagram.id)
        assert deleted_diagram is None

@patch('os.path.exists', return_value=True)
@patch('os.remove')
def test_delete_pool_multiple_diagrams(mock_remove, mock_exists, client, app, ve_user): # pylint: disable=W0613
    """Test ID: UT-181
    Test multiple diagrams are deleted when deleting a pool.

    This test ensures that all diagrams associated with a pool are deleted
    from both the server and the database.

    Args:
        mock_remove: Mock for os.remove to simulate file removal.
        mock_exists: Mock for os.path.exists to simulate existing files.
        client: The test client instance.
        app: The Flask application instance.

    Asserts:
        - All diagram files are deleted from the server.
        - All diagram records are removed from the database.
        - The response status code is 200.
    """
    login(client, ve_user.username, 'vepassword')

    with app.app_context():
        # Create a test pool and multiple diagrams
        pool = Pool(name="Test Pool", element="2",
                    start_date=datetime.now(),
                    end_date=datetime.now())
        db.session.add(pool)
        db.session.flush()

        diagrams = [
            ExamDiagram(pool_id=pool.id, name="Diagram 1", path="diagrams/1.png"),
            ExamDiagram(pool_id=pool.id, name="Diagram 2", path="diagrams/2.png"),
        ]
        db.session.bulk_save_objects(diagrams)
        db.session.flush()

        # DELETE request to remove the pool and diagrams
        response = client.delete(f'/ve/delete_pool/{pool.id}', follow_redirects=True)

    # Assert the request was successful
    assert response.status_code == 200

    # Verify that both diagram files were removed
    mock_remove.assert_any_call(os.path.join(app.config['UPLOAD_FOLDER'], "1.png"))
    mock_remove.assert_any_call(os.path.join(app.config['UPLOAD_FOLDER'], "2.png"))

    # Verify that both diagrams were removed from the database
    with app.app_context():
        remaining_diagrams = ExamDiagram.query.filter_by(pool_id=pool.id).all()
        assert len(remaining_diagrams) == 0

def test_delete_pool_no_diagrams(client, app, ve_user):
    """Test ID: UT-182
    Test pool deletion when there are no diagrams associated with the pool.

    This test ensures that the pool is deleted successfully, even if no diagrams are linked.

    Args:
        client: The test client instance.
        app: The Flask application instance.
        ve_user: The VE user fixture.

    Asserts:
        - The pool is removed from the database.
        - The response status code is 200.
    """
    login(client, ve_user.username, 'vepassword')

    with app.app_context():
        # Create a pool with no diagrams
        pool = Pool(name="Test Pool", element="2",
                    start_date=datetime.now(),
                    end_date=datetime.now())
        db.session.add(pool)
        db.session.flush()

        # DELETE request to remove the pool
        response = client.delete(f'/ve/delete_pool/{pool.id}', follow_redirects=True)

    # Assert the request was successful
    assert response.status_code == 200

    # Verify the pool was removed from the database
    with app.app_context():
        deleted_pool = db.session.get(Pool, pool.id)
        assert deleted_pool is None