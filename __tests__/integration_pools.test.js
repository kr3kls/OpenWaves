/**
 * File: pools.test.js
 * 
 * Description: This file contains integration tests for the pools page functionality.
 * 
 * @jest-environment jsdom
 */


describe('Pool management functionality', () => {
    let csrfTokenInput;
    let poolRow, expandableRow;

    beforeEach(() => {
        // Replace location.reload with a mock function
        delete window.location;  // JSDOM allows deleting `location` for assignment
        window.location = { reload: jest.fn() };

        // Mock window.location.reload to prevent navigation errors in jsdom
        Object.defineProperty(window, 'location', {
            writable: true,
            value: { reload: jest.fn() }, // Mock reload method
        });
    
        // Set up the DOM structure, including the required elements
        document.body.innerHTML = `
        <div class="container has-text-centered">
            <!-- Flash messages -->
            <div class="column is-8 is-offset-2">
                <div class="box">
                    <h3 class="title has-text-centered has-text-dark">Question Pools</h3>
                    <div class="table-container has-text-centered">
                        <table class="table is-striped is-hoverable is-fullwidth">
                        <thead>
                            <tr>
                                <th>Pool ID</th>
                                <th>Pool Name</th>
                                <th>Element</th>
                                <th>Start Date</th>
                                <th>End Date</th>
                                <th>Questions</th>
                            </tr>
                        </thead>
                        
                        <tbody>
                            
                            <tr class="pool-row" data-id="1">
                                <td>1</td>
                                <td>Technician</td>
                                <td>2</td>
                                <td>2024-07-01</td>
                                <td>2028-06-30</td>
                                <td>
                                    
                                        411 questions
                                    
                                </td>
                                <td>
                                    <button class="button is-small is-danger delete-pool-button" data-name="Technician" data-id="1">Delete</button>
                                </td>
                            </tr>
                            <tr class="expandable-row" data-id="1">
                                <td colspan="7">
                                    <div id="fullscreen-overlay" class="fullscreen-overlay">
                                            <img id="fullscreen-image" class="fullscreen-image" src="" alt="Blown-up Diagram">
                                        </div><table class="table is-striped is-fullwidth">
                                        <thead>
                                            <tr>
                                                <th>Diagram ID</th>
                                                <th>Diagram Name</th>
                                                <th>Image</th>
                                            </tr>
                                        </thead>
                                        
                                        <tbody>
                                            
                                            
                                            <tr>
                                                <td>1</td>
                                                <td>T-1</td>
                                                <td><img src="/static/images/diagrams/1_T1.jpg" alt="T-1" class="pool-diagram thumbnail-image"></td>
                                                <td>
                                                    <button class="button is-small is-danger delete-diagram-button" data-name="diagrams/1_T1.jpg" data-id="1">Delete</button>
                                                </td>
                                            </tr>
                                            
                                            <tr>
                                                <td colspan="4">
                                                    <button class="button is-small is-light-button-color upload-diagram-button" data-name="Technician" data-id="1">Upload</button>
                                                </td>
                                            </tr>
                                            
                                    </tbody></table>
                                    <!-- Modal for CSV and Image upload for this pool -->
                                    <div class="modal" id="upload-modal-1">
                                        <div class="modal-background"></div>
                                        <div class="modal-card">
                                            <header class="modal-card-head">
                                                <p class="modal-card-title">Upload Diagram for Technician</p>
                                                <button class="delete close-modal" aria-label="close"></button>
                                            </header>
                                            <section class="modal-card-body">
                                                <form id="upload-form-1" enctype="multipart/form-data">
                                                    
                                                        <input type="hidden" name="csrf_token" value="dummy-csrf-token">
                                                    

                                                    <!-- Diagram Name Field (Readonly) -->
                                                    <div class="field">
                                                        <label class="label">Diagram Name</label>
                                                        <div class="control">
                                                            <input class="input" type="text" name="diagram_name" value="">
                                                        </div>
                                                        <p class="help">Please enter the diagram name based on the element and current number (e.g., T-1, G-1, E-1).</p>
                                                    </div>

                                                    <!-- Upload Image File Field -->
                                                    <div class="field">
                                                        <label class="label">Upload Image File</label>
                                                        <div class="control">
                                                            <input class="input" type="file" name="file" accept="image/*" required="">
                                                        </div>
                                                    </div>
                                                </form>
                                            </section>
                                            <footer class="modal-card-foot">
                                                <button class="button is-success submit-upload" data-pool-id="1">Upload</button>
                                                <button class="button close-modal">Cancel</button>
                                            </footer>
                                        </div>
                                    </div>
                                    
                            </td></tr><tr class="pool-row" data-id="2">
                                <td>2</td>
                                <td>General</td>
                                <td>3</td>
                                <td>2024-07-01</td>
                                <td>2028-06-30</td>
                                <td>
                                    
                                        427 questions
                                    
                                </td>
                                <td>
                                    <button class="button is-small is-danger delete-pool-button" data-name="General" data-id="2">Delete</button>
                                </td>
                            </tr>
                            <tr class="expandable-row" data-id="2">
                                <td colspan="7">
                                    <div id="fullscreen-overlay" class="fullscreen-overlay">
                                            <img id="fullscreen-image" class="fullscreen-image" src="" alt="Blown-up Diagram">
                                        </div><table class="table is-striped is-fullwidth">
                                        <thead>
                                            <tr>
                                                <th>Diagram ID</th>
                                                <th>Diagram Name</th>
                                                <th>Image</th>
                                            </tr>
                                        </thead>
                                        
                                        <tbody>
                                            
                                            <tr>
                                                <td colspan="4">No diagrams found.</td>
                                                <td>
                                                    <button class="button is-small is-light-button-color upload-diagram-button" data-name="General" data-id="2">Upload</button>
                                                </td>
                                            </tr>
                                            
                                    </tbody></table>
                                    <!-- Modal for CSV and Image upload for this pool -->
                                    <div class="modal" id="upload-modal-2">
                                        <div class="modal-background"></div>
                                        <div class="modal-card">
                                            <header class="modal-card-head">
                                                <p class="modal-card-title">Upload Diagram for General</p>
                                                <button class="delete close-modal" aria-label="close"></button>
                                            </header>
                                            <section class="modal-card-body">
                                                <form id="upload-form-2" enctype="multipart/form-data">
                                                    
                                                        <input type="hidden" name="csrf_token" value="dummy-csrf-token">
                                                    

                                                    <!-- Diagram Name Field (Readonly) -->
                                                    <div class="field">
                                                        <label class="label">Diagram Name</label>
                                                        <div class="control">
                                                            <input class="input" type="text" name="diagram_name" value="">
                                                        </div>
                                                        <p class="help">Please enter the diagram name based on the element and current number (e.g., T-1, G-1, E-1).</p>
                                                    </div>

                                                    <!-- Upload Image File Field -->
                                                    <div class="field">
                                                        <label class="label">Upload Image File</label>
                                                        <div class="control">
                                                            <input class="input" type="file" name="file" accept="image/*" required="">
                                                        </div>
                                                    </div>
                                                </form>
                                            </section>
                                            <footer class="modal-card-foot">
                                                <button class="button is-success submit-upload" data-pool-id="2">Upload</button>
                                                <button class="button close-modal">Cancel</button>
                                            </footer>
                                        </div>
                                    </div>
                                    
                            </td></tr><tr class="pool-row" data-id="3">
                                <td>3</td>
                                <td>Extra</td>
                                <td>4</td>
                                <td>2024-07-01</td>
                                <td>2028-06-30</td>
                                <td>
                                    
                                        <!-- Display upload button when there are no questions -->
                                        <button class="button is-small is-light-button-color" id="upload-button-3">Upload Questions</button>
                        
                                        <!-- Modal for CSV upload -->
                                        <div class="modal" id="upload-modal-3">
                                            <div class="modal-background"></div>
                                            <div class="modal-card">
                                                <header class="modal-card-head">
                                                    <p class="modal-card-title">Upload Questions for Extra</p>
                                                    <button class="delete" aria-label="close"></button>
                                                </header>
                                                <section class="modal-card-body">
                                                    <form id="upload-form-3" enctype="multipart/form-data">
                                                        
                                                            <input type="hidden" name="csrf_token" value="dummy-csrf-token">
                                                        
                                                        
                                                        <div class="field">
                                                            <label class="label">Upload CSV File</label>
                                                            <div class="control">
                                                                <input class="input" type="file" name="file" accept=".csv" required="">
                                                            </div>
                                                        </div>
                                                    </form>
                                                </section>
                                                <footer class="modal-card-foot">
                                                    <button class="button is-light-button-color" id="submit-upload-3">Upload</button>
                                                    <button class="button is-button-color">Cancel</button>
                                                </footer>
                                            </div>
                                        </div>
                                    
                                </td>
                                <td>
                                    <button class="button is-small is-danger delete-pool-button" data-name="Extra" data-id="3">Delete</button>
                                </td>
                            </tr>
                            <tr class="expandable-row" data-id="3">
                                <td colspan="7">
                                    <div id="fullscreen-overlay" class="fullscreen-overlay">
                                            <img id="fullscreen-image" class="fullscreen-image" src="" alt="Blown-up Diagram">
                                        </div><table class="table is-striped is-fullwidth">
                                        <thead>
                                            <tr>
                                                <th>Diagram ID</th>
                                                <th>Diagram Name</th>
                                                <th>Image</th>
                                            </tr>
                                        </thead>
                                        
                                        <tbody>
                                            
                                            <tr>
                                                <td colspan="4">No diagrams found.</td>
                                                <td>
                                                    <button class="button is-small is-light-button-color upload-diagram-button" data-name="Extra" data-id="3">Upload</button>
                                                </td>
                                            </tr>
                                            
                                    </tbody></table>
                                    <!-- Modal for CSV and Image upload for this pool -->
                                    <div class="modal" id="upload-modal-3">
                                        <div class="modal-background"></div>
                                        <div class="modal-card">
                                            <header class="modal-card-head">
                                                <p class="modal-card-title">Upload Diagram for Extra</p>
                                                <button class="delete close-modal" aria-label="close"></button>
                                            </header>
                                            <section class="modal-card-body">
                                                <form id="upload-form-3" enctype="multipart/form-data">
                                                    
                                                        <input type="hidden" name="csrf_token" value="dummy-csrf-token">
                                                    

                                                    <!-- Diagram Name Field (Readonly) -->
                                                    <div class="field">
                                                        <label class="label">Diagram Name</label>
                                                        <div class="control">
                                                            <input class="input" type="text" name="diagram_name" value="">
                                                        </div>
                                                        <p class="help">Please enter the diagram name based on the element and current number (e.g., T-1, G-1, E-1).</p>
                                                    </div>

                                                    <!-- Upload Image File Field -->
                                                    <div class="field">
                                                        <label class="label">Upload Image File</label>
                                                        <div class="control">
                                                            <input class="input" type="file" name="file" accept="image/*" required="">
                                                        </div>
                                                    </div>
                                                </form>
                                            </section>
                                            <footer class="modal-card-foot">
                                                <button class="button is-success submit-upload" data-pool-id="3">Upload</button>
                                                <button class="button close-modal">Cancel</button>
                                            </footer>
                                        </div>
                                    </div>
                                    
                                </td>
                            </tr>                
                        </tbody>
                        
                        </table>
                    </div>

                    <!-- Button to create a new pool -->
                    <div class="has-text-centered">
                        <button class="button is-button-color" id="create-pool-button">Create New Pool</button>
                    </div>

                    <!-- Modal for creating a new question pool -->
                    <div class="modal" id="create-pool-modal">
                        <div class="modal-background"></div>
                        <div class="modal-card">
                            <header class="modal-card-head">
                                <p class="modal-card-title">Create Question Pool</p>
                                <button class="delete close-modal" aria-label="close"></button>
                            </header>
                            <section class="modal-card-body">
                                <form id="create-pool-form">
                                    
                                        <input type="hidden" name="csrf_token" value="dummy-csrf-token">
                                    

                                    <!-- Dropdown for Pool Name -->
                                    <div class="field">
                                        <label class="label">Element Pool</label>
                                        <div class="control">
                                            <div class="select">
                                                <select id="pool-name" name="pool_name" required="">
                                                    <option value="Technician">Technician</option>
                                                    <option value="General">General</option>
                                                    <option value="Extra">Extra</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Hidden Element field that gets auto-filled -->
                                    <input type="hidden" id="exam-element" name="exam_element" value="2">

                                    <!-- Auto-populated Start Date -->
                                    <div class="field">
                                        <label class="label">Start Date</label>
                                        <div class="control">
                                            <input class="input" type="date" id="start-date" name="start_date" required="">
                                        </div>
                                    </div>

                                    <!-- Auto-populated End Date -->
                                    <div class="field">
                                        <label class="label">End Date</label>
                                        <div class="control">
                                            <input class="input" type="date" id="end-date" name="end_date" required="">
                                        </div>
                                    </div>
                                </form>
                            </section>
                            <footer class="modal-card-foot">
                                <button class="button is-success" id="submit-pool-form">Save</button>
                                <button class="button is-light" id="cancel-pool-form">Cancel</button>
                            </footer>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        `;

        // Mock console.error to track errors
        console.error = jest.fn();

        csrfTokenInput = document.querySelector('input[name="csrf_token"]');
        
        // Mock window.confirm and window.alert to prevent actual prompts during tests
        jest.spyOn(window, 'confirm').mockImplementation(() => true);
        jest.spyOn(window, 'alert').mockImplementation(() => {});
        jest.spyOn(console, 'error').mockImplementation(() => {});
    
        // Mock fetch API
        global.fetch = jest.fn(() => Promise.resolve({ ok: true }));

        // Require pools.js in an isolated module context
        jest.isolateModules(() => {
            require('../openwaves/static/js/pools');
        });

        // Simulate DOMContentLoaded to initialize event listeners
        document.dispatchEvent(new Event('DOMContentLoaded'));

        // Now assign poolRow and expandableRow after event listeners are attached
        poolRow = document.querySelector('.pool-row');
        expandableRow = document.querySelector('.expandable-row');

        consoleErrorMock = jest.spyOn(console, 'error').mockImplementation(() => {});
    });
        
    afterEach(() => {
        jest.resetModules();
        jest.clearAllMocks();
        document.body.innerHTML = '';
    });

    /**
     * Test ID: IT-152
     * Test the functionality of the delete pool button when the request is successful.
     *
     * This test ensures that clicking the delete pool button triggers a DELETE request 
     * and shows a success alert when the request completes successfully.
     *
     * Asserts:
     * - A DELETE request is sent to the correct URL with appropriate headers.
     * - A success alert is shown to the user.
     */
    test('delete pool button triggers fetch and shows success alert', async () => {
        const deleteButton = document.querySelector('.delete-pool-button');
        deleteButton.click();
        await Promise.resolve();

        expect(fetch).toHaveBeenCalledWith('/ve/delete_pool/1', {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': 'dummy-csrf-token',
                'Content-Type': 'application/json',
            },
        });
        expect(window.alert).toHaveBeenCalledWith('Pool deleted successfully.');
    });

    /**
     * Test ID: IT-153
     * Test the behavior of the delete pool button when the fetch request is rejected.
     *
     * This test ensures that when the delete request fails due to a network error, 
     * an appropriate error message is displayed to the user, and the error is logged.
     *
     * Asserts:
     * - An error alert is shown to the user when the fetch request is rejected.
     * - The console.error is called with the correct error message.
     */
    test('delete pool button handles fetch rejection gracefully', async () => {
        // Mock fetch to reject with an error
        const mockError = new Error('Network error');
        fetch.mockRejectedValueOnce(mockError);
    
        // Reference the delete button
        const deleteButton = document.querySelector('.delete-pool-button');
        
        // Add a console log to verify the button click is being called
        deleteButton.click();
    
        // Wait for all asynchronous code to complete
        await new Promise((resolve) => setTimeout(resolve, 0));
    
        // Ensure that the correct alert message is displayed
        expect(window.alert).toHaveBeenCalledWith('There was an error deleting the pool.');
    
        // Ensure that console.error is called with the error
        expect(console.error).toHaveBeenCalledWith('Error:', mockError);
    });   

    /**
     * Test ID: IT-154
     * Test the behavior of the delete pool button when the server returns a non-OK response.
     *
     * This test ensures that when the server returns a non-OK response (e.g., 400 or 500 status),
     * an appropriate error alert is shown to the user indicating that there was an error deleting the pool.
     *
     * Asserts:
     * - An error alert is shown to the user when the server responds with a non-OK status.
     */
    test('delete pool button triggers error alert on fetch failure', async () => {
        global.fetch = jest.fn(() => Promise.resolve({ ok: false }));  // Mock a failure response
        const deleteButton = document.querySelector('.delete-pool-button');
        deleteButton.click();
        await Promise.resolve();

        expect(window.alert).toHaveBeenCalledWith('There was an error deleting the pool.');
    });

    /**
     * Test ID: IT-155
     * Test the behavior of the upload form submission when the server response is non-OK.
     *
     * This test ensures that when the server returns a non-OK response, an appropriate error message 
     * is displayed, and the modal remains closed after submission.
     *
     * Asserts:
     * - A POST request is sent to the correct URL with appropriate form data.
     * - An error alert is shown to the user.
     * - The modal is closed after the submission fails.
     */
    test('submit upload form handles non-OK response', async () => {
        const modal = document.getElementById('upload-modal-3');
        const submitButton = document.getElementById('submit-upload-3');
        
        // Mock fetch to return ok: false
        global.fetch = jest.fn(() => Promise.resolve({ ok: false }));
        
        // Simulate form submission
        submitButton.click();
        
        // Wait for the asynchronous code to complete
        await Promise.resolve();
        
        // Use toHaveBeenNthCalledWith to verify the specific call to fetch
        expect(fetch).toHaveBeenNthCalledWith(1, '/ve/upload_questions/3', {
            method: 'POST',
            body: expect.any(FormData),
        });

        // Assert that the error alert is shown
        expect(window.alert).toHaveBeenCalledWith('There was an error uploading the questions.');

        // The modal should still be closed after submission
        expect(modal.classList.contains('is-active')).toBe(false);
    });
    
    /**
     * Test ID: IT-156
     * Test the successful submission of the upload form.
     *
     * This test ensures that when the upload form is successfully submitted, a POST request 
     * is made with the correct data, and the modal is closed after a successful response.
     *
     * Asserts:
     * - A POST request is sent to the correct URL with appropriate form data.
     * - The modal is closed after the submission succeeds.
     */
    test('submit upload form triggers fetch and closes modal', async () => {
        const modal = document.getElementById('upload-modal-3');
        const submitButton = document.getElementById('submit-upload-3');
        
        const form = document.getElementById('upload-form-3');
        const formData = new FormData(form);

        // Mock the global fetch to return a successful response
        global.fetch = jest.fn(() => Promise.resolve({ ok: true }));

        // Simulate form submission
        submitButton.click();
        await new Promise((resolve) => setTimeout(resolve, 0)); // Wait for asynchronous code to complete

        // Ensure that the fetch was called correctly
        expect(fetch).toHaveBeenNthCalledWith(1, '/ve/upload_questions/3', {
            method: 'POST',
            body: expect.any(FormData),
        });

        // Assert that the modal is no longer active (closed)
        expect(modal.classList.contains('is-active')).toBe(false);
    });

    /**
     * Test ID: IT-157
     * Test the functionality of submitting the create pool form.
     *
     * This test ensures that when the create pool form is submitted, a fetch request
     * is triggered, and the modal is properly closed after the submission.
     *
     * Asserts:
     * - A POST request is made to the correct URL with appropriate data.
     * - The modal is closed after the form submission.
     * - An alert is shown if the pool is created successfully.
     * - The page is reloaded after successful creation.
     */
    test('submit pool form triggers fetch, shows alert, reloads, and closes modal', async () => {
        const modal = document.getElementById('create-pool-modal');
        const createPoolForm = document.getElementById('create-pool-form');
        const submitPoolFormButton = document.getElementById('submit-pool-form');

        modal.classList.add('is-active');

        // Mock global fetch to return a successful response
        global.fetch = jest.fn(() =>
            Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ success: true }),
            })
        );

        // Mock window.alert
        window.alert = jest.fn();

        // Mock window.location.reload
        delete window.location;
        window.location = { reload: jest.fn() };

        // Trigger form submission
        submitPoolFormButton.click();
        await Promise.resolve(); // Wait for the fetch call to resolve

        // Assertions
        expect(fetch).toHaveBeenCalledWith('/ve/create_pool', expect.any(Object));

        // Assert alert is shown
        expect(window.alert).toHaveBeenCalledWith('Pool created successfully!');

        // Assert location.reload is called
        expect(window.location.reload).toHaveBeenCalled();

        // Assert modal is closed
        expect(modal.classList.contains('is-active')).toBe(false);
    });

    /**
     * Test ID: IT-158
     * Test the behavior of submitting the pool form when the server response is non-OK.
     *
     * This test ensures that when a user attempts to submit the pool creation form
     * and receives a non-OK response, an appropriate error message is displayed
     * and the modal is closed.
     *
     * Asserts:
     * - The server is called with the correct parameters.
     * - An error alert is shown to the user.
     * - The pool creation modal is closed after submission.
     */
    test('submit pool form handles non-OK response', async () => {
        const modal = document.getElementById('create-pool-modal');
        const submitPoolFormButton = document.getElementById('submit-pool-form');
    
        modal.classList.add('is-active');
    
        // Mock fetch to return ok: false
        global.fetch = jest.fn(() => Promise.resolve({ ok: false }));
    
        submitPoolFormButton.click();
        await Promise.resolve();
    
        expect(fetch).toHaveBeenCalledWith('/ve/create_pool', expect.any(Object));
    
        expect(window.alert).toHaveBeenCalledWith('There was an error creating the pool.');
    
        // Check that the modal is closed after submission
        expect(modal.classList.contains('is-active')).toBe(false);
    });

    /**
     * Test ID: IT-159
     * Test the functionality of handling the upload submission in the modal.
     *
     * This test ensures that clicking the upload button sends a POST request,
     * shows an alert upon success, and closes the modal.
     *
     * Asserts:
     * - A POST request is made to the correct URL with the appropriate form data.
     * - The success alert is shown to the user.
     * - The modal is closed after submission.
     */
    test('handle upload submission and close modal upon successful response', async () => {
        // Reference the modal and the upload button inside the modal
        const modal = document.getElementById('upload-modal-1');
        const submitUploadButton = document.querySelector('.submit-upload[data-pool-id="1"]');
        const form = document.getElementById('upload-form-1');
        const formData = new FormData(form);

        // Ensure the modal starts as active (open)
        modal.classList.add('is-active');
        expect(modal.classList.contains('is-active')).toBe(true);

        // Mock the fetch API to simulate a successful response
        global.fetch = jest.fn(() => Promise.resolve({ ok: true }));

        // Simulate clicking the submit upload button
        submitUploadButton.click();

        // Wait for asynchronous actions to complete
        await new Promise(resolve => setTimeout(resolve, 0));

        // Assert that a POST request was made with the correct URL and data
        expect(fetch).toHaveBeenCalledWith('/ve/upload_diagram/1', {
            method: 'POST',
            body: expect.any(FormData),
        });

        // Assert that the success alert is shown
        expect(window.alert).toHaveBeenCalledWith('Diagram uploaded successfully!');

        // Assert that the modal is closed after submission
        expect(modal.classList.contains('is-active')).toBe(false);
    });

    /**
     * Test ID: IT-160
     * Test the functionality of the delete diagram button when the request is successful.
     *
     * This test ensures that clicking the delete diagram button triggers a DELETE request 
     * and shows a success alert when the request completes successfully.
     *
     * Asserts:
     * - A DELETE request is sent to the correct URL with appropriate headers.
     * - A success alert is shown to the user.
     * - The page is reloaded after successful deletion.
     */
    test('delete diagram button triggers fetch and shows success alert', async () => {
        const deleteButton = document.querySelector('.delete-diagram-button');
        deleteButton.click();
        await Promise.resolve();

        expect(fetch).toHaveBeenCalledWith('/ve/delete_diagram/1', {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': 'dummy-csrf-token',
                'Content-Type': 'application/json',
            },
        });
        expect(window.alert).toHaveBeenCalledWith('Diagram deleted successfully.');
        expect(window.location.reload).toHaveBeenCalled();
    });

    /**
     * Test ID: IT-161
     * Test the behavior of the delete diagram button when the fetch request is rejected.
     *
     * This test ensures that when the delete request fails due to a network error, 
     * an appropriate error message is displayed to the user, and the error is logged.
     *
     * Asserts:
     * - An error alert is shown to the user when the fetch request is rejected.
     * - The console.error is called with the correct error message.
     */
    test('delete diagram button handles fetch rejection gracefully', async () => {
        const mockError = new Error('Network error');
        fetch.mockRejectedValueOnce(mockError);

        const deleteButton = document.querySelector('.delete-diagram-button');
        deleteButton.click();
        await new Promise(resolve => setTimeout(resolve, 0));

        expect(window.alert).toHaveBeenCalledWith('There was an error deleting the diagram.');
        expect(console.error).toHaveBeenCalledWith('Error:', mockError);
    });

    /**
     * Test ID: IT-162
     * Test the behavior of the delete diagram button when the server returns a non-OK response.
     *
     * This test ensures that when the server returns a non-OK response (e.g., 400 or 500 status),
     * an appropriate error alert is shown to the user.
     *
     * Asserts:
     * - An error alert is shown to the user when the server responds with a non-OK status.
     */
    test('delete diagram button triggers error alert on fetch failure', async () => {
        global.fetch = jest.fn(() => Promise.resolve({ ok: false }));
        const deleteButton = document.querySelector('.delete-diagram-button');
        deleteButton.click();
        await Promise.resolve();

        expect(window.alert).toHaveBeenCalledWith('There was an error deleting the diagram.');
    });
});
