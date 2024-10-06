/**
 * File: pools.test.js
 * 
 * Description: This file contains tests for the pools page functionality.
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
                                                <th>Path</th>
                                            </tr>
                                        </thead>
                                        
                                        <tbody>
                                            
                                            
                                            <tr>
                                                <td>1</td>
                                                <td>T-1</td>
                                                <td><img src="/static/images/diagrams/1_T1.jpg" alt="T-1" class="pool-diagram thumbnail-image"></td>
                                                <td>diagrams/1_T1.jpg</td>
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
                                    
                                        <!-- Display upload button when there are no questions -->
                                        <button class="button is-small is-light-button-color" id="upload-button-2">Upload Questions</button>
                        
                                        <!-- Modal for CSV upload -->
                                        <div class="modal" id="upload-modal-2">
                                            <div class="modal-background"></div>
                                            <div class="modal-card">
                                                <header class="modal-card-head">
                                                    <p class="modal-card-title">Upload Questions for General</p>
                                                    <button class="delete" aria-label="close"></button>
                                                </header>
                                                <section class="modal-card-body">
                                                    <form id="upload-form-2" enctype="multipart/form-data">
                                                        
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
                                                    <button class="button is-light-button-color" id="submit-upload-2">Upload</button>
                                                    <button class="button is-button-color">Cancel</button>
                                                </footer>
                                            </div>
                                        </div>
                                    
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
                                                <th>Path</th>
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
     * Test ID: UT-123
     * Test the functionality of the delete pool button when the request is successful.
     *
     * This test ensures that clicking the delete pool button triggers a DELETE request 
     * and shows a success alert when the request completes successfully.
     *
     * Asserts:
     * - A DELETE request is sent to the correct URL with appropriate headers.
     * - A success alert is shown to the user.
     */
    test('UT-123: delete pool button triggers fetch and shows success alert', async () => {
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
     * Test ID: UT-124
     * Test the behavior of the delete pool button when the fetch request is rejected.
     *
     * This test ensures that when the delete request fails due to a network error, 
     * an appropriate error message is displayed to the user, and the error is logged.
     *
     * Asserts:
     * - An error alert is shown to the user when the fetch request is rejected.
     * - The console.error is called with the correct error message.
     */
    test('UT-124: delete pool button handles fetch rejection gracefully', async () => {
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
     * Test ID: UT-125
     * Test the behavior of the delete pool button when the server returns a non-OK response.
     *
     * This test ensures that when the server returns a non-OK response (e.g., 400 or 500 status),
     * an appropriate error alert is shown to the user indicating that there was an error deleting the pool.
     *
     * Asserts:
     * - An error alert is shown to the user when the server responds with a non-OK status.
     */
    test('UT-125: delete pool button triggers error alert on fetch failure', async () => {
        global.fetch = jest.fn(() => Promise.resolve({ ok: false }));  // Mock a failure response
        const deleteButton = document.querySelector('.delete-pool-button');
        deleteButton.click();
        await Promise.resolve();

        expect(window.alert).toHaveBeenCalledWith('There was an error deleting the pool.');
    });

    /**
     * Test ID: UT-126
     * Test the functionality of the upload button triggering modal visibility.
     *
     * This test ensures that clicking the upload button opens the corresponding modal, 
     * allowing users to interact with the upload form.
     *
     * Asserts:
     * - The modal becomes active (is shown) after clicking the upload button.
     */
    test('UT-126: upload button triggers modal visibility', () => {
        const uploadButton = document.getElementById('upload-button-2');
        const modal = document.getElementById('upload-modal-2');
        
        // Simulate clicking the upload button
        uploadButton.click();
        
        // Assert the modal becomes active
        expect(modal.classList.contains('is-active')).toBe(true);
    });

    /**
     * Test ID: UT-127
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
    test('UT-127: submit upload form handles non-OK response', async () => {
        const modal = document.getElementById('upload-modal-2');
        const submitButton = document.getElementById('submit-upload-2');
        
        // Mock fetch to return ok: false
        global.fetch = jest.fn(() => Promise.resolve({ ok: false }));
        
        // Simulate form submission
        submitButton.click();
        
        // Wait for the asynchronous code to complete
        await Promise.resolve();
        
        // Use toHaveBeenNthCalledWith to verify the specific call to fetch
        expect(fetch).toHaveBeenNthCalledWith(1, '/ve/upload_questions/2', {
            method: 'POST',
            body: expect.any(FormData),
        });

        // Assert that the error alert is shown
        expect(window.alert).toHaveBeenCalledWith('There was an error uploading the questions.');

        // The modal should still be closed after submission
        expect(modal.classList.contains('is-active')).toBe(false);
    });
    
    /**
     * Test ID: UT-128
     * Test the successful submission of the upload form.
     *
     * This test ensures that when the upload form is successfully submitted, a POST request 
     * is made with the correct data, and the modal is closed after a successful response.
     *
     * Asserts:
     * - A POST request is sent to the correct URL with appropriate form data.
     * - The modal is closed after the submission succeeds.
     */
    test('UT-128: submit upload form triggers fetch and closes modal', async () => {
        const modal = document.getElementById('upload-modal-2');
        const submitButton = document.getElementById('submit-upload-2');
        
        const form = document.getElementById('upload-form-2');
        const formData = new FormData(form);

        // Mock the global fetch to return a successful response
        global.fetch = jest.fn(() => Promise.resolve({ ok: true }));

        // Simulate form submission
        submitButton.click();
        await new Promise((resolve) => setTimeout(resolve, 0)); // Wait for asynchronous code to complete

        // Ensure that the fetch was called correctly
        expect(fetch).toHaveBeenNthCalledWith(1, '/ve/upload_questions/2', {
            method: 'POST',
            body: expect.any(FormData),
        });

        // Assert that the modal is no longer active (closed)
        expect(modal.classList.contains('is-active')).toBe(false);
    });

    /**
     * Test ID: UT-129
     * Test the functionality of closing the modal when the cancel button is clicked.
     *
     * This test ensures that clicking the cancel button properly closes the create pool modal,
     * preventing any unintended interactions while the modal is open.
     *
     * Asserts:
     * - The modal starts as active (open).
     * - The modal is closed after the cancel button is clicked.
     */
    test('UT-129: close create-pool-modal when cancel is clicked', () => {
        // Get the close button (X) and the modal from the DOM
        const cancelButton = document.querySelector('#cancel-pool-form'); // Cancel button class
        const modal = document.getElementById('create-pool-modal');
    
        // Ensure the modal starts as active (open)
        modal.classList.add('is-active'); // This opens the modal
    
        // Ensure the modal is actually open before closing
        expect(modal.classList.contains('is-active')).toBe(true);
    
        // Try to close with the cancel button
        cancelButton.click(); 
    
        // Assert the modal is no longer active (closed)
        expect(modal.classList.contains('is-active')).toBe(false);
    });

    /**
     * Test ID: UT-130
     * Test the functionality of closing the modal when the close button (X) is clicked.
     *
     * This test ensures that clicking the close button properly closes the create pool modal,
     * preventing any unintended interactions while the modal is open.
     *
     * Asserts:
     * - The modal starts as active (open).
     * - The modal is closed after the close button is clicked.
     */
    test('UT-130: close create-pool-modal when X is clicked', async () => {    
        const closeButton = document.querySelector('#create-pool-modal .delete');
        const modal = document.getElementById('create-pool-modal');
    
        // Open the modal
        modal.classList.add('is-active');
    
        // Ensure the modal starts as active (open)
        expect(modal.classList.contains('is-active')).toBe(true);
    
        // Simulate the click event
        closeButton.click();
    
        // Wait for any asynchronous actions to complete (this ensures that event listeners are executed)
        await new Promise((resolve) => setTimeout(resolve, 0));
    
        // Assert that the modal is no longer active
        expect(modal.classList.contains('is-active')).toBe(false);
    });

    /**
     * Test ID: UT-131
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
    test('UT-131: submit pool form triggers fetch, shows alert, reloads, and closes modal', async () => {
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
     * Test ID: UT-132
     * Test that changing the start date automatically updates the end date.
     *
     * This test ensures that when the start date is changed, the end date is
     * automatically updated to 4 years later, with the end date always set to June 30.
     *
     * Asserts:
     * - The end date is correctly updated based on the new start date.
     */
    test('UT-132: start date change updates end date automatically', () => {
        const startDateField = document.getElementById('start-date');
        const endDateField = document.getElementById('end-date');

        startDateField.value = '2023-06-30';
        const changeEvent = new Event('change');
        startDateField.dispatchEvent(changeEvent);

        const expectedEndDate = new Date('2023-06-30');
        expectedEndDate.setFullYear(expectedEndDate.getFullYear() + 4);
        const expectedFormattedEndDate = expectedEndDate.toISOString().split('T')[0];

        expect(endDateField.value).toBe(expectedFormattedEndDate);
    });

    /**
     * Test ID: UT-133
     * Test the functionality of the create pool button.
     *
     * This test ensures that clicking the create pool button sets the default
     * start and end dates for the pool and opens the create pool modal.
     *
     * Asserts:
     * - The start date is set to July 1 of the current year.
     * - The end date is set to June 30, 4 years from the start date.
     * - The create pool modal is opened after clicking the create pool button.
     */
    test('UT-133: create pool button sets default dates and opens modal', () => {
        const createPoolButton = document.getElementById('create-pool-button');
        const createPoolModal = document.getElementById('create-pool-modal');
        const startDateField = document.getElementById('start-date');
        const endDateField = document.getElementById('end-date');
    
        // Simulate clicking the create pool button
        createPoolButton.click();
    
        const currentYear = new Date().getFullYear();
        expect(startDateField.value).toBe(`${currentYear}-07-01`);
        expect(endDateField.value).toBe(`${currentYear + 4}-06-30`);
    
        // Check that the modal is opened
        expect(createPoolModal.classList.contains('is-active')).toBe(true);
    });
    
    /**
     * Test ID: UT-134
     * Test the functionality of selecting a pool name.
     *
     * This test ensures that selecting the 'Technician' pool name updates the exam
     * element field with the correct value.
     *
     * Asserts:
     * - Selecting 'Technician' updates the exam element field to '2'.
     */
    test('UT-134: pool name selection updates exam element to 2 for Technician', () => {
        const poolNameDropdown = document.getElementById('pool-name');
        const examElementField = document.getElementById('exam-element');
    
        poolNameDropdown.value = 'Technician';
        const changeEvent = new Event('change');
        poolNameDropdown.dispatchEvent(changeEvent);
    
        expect(examElementField.value).toBe('2');
    });
    
    /**
     * Test ID: UT-135
     * Test the functionality of selecting the 'General' pool name.
     *
     * This test ensures that selecting the 'General' pool name updates the exam
     * element field with the correct value.
     *
     * Asserts:
     * - Selecting 'General' updates the exam element field to '3'.
     */
    test('UT-135: pool name selection updates exam element to 3 for General', () => {
        const poolNameDropdown = document.getElementById('pool-name');
        const examElementField = document.getElementById('exam-element');

        poolNameDropdown.value = 'General';
        const changeEvent = new Event('change');
        poolNameDropdown.dispatchEvent(changeEvent);

        expect(examElementField.value).toBe('3');
    });

    /**
     * Test ID: UT-136
     * Test the functionality of selecting the 'Extra' pool name.
     *
     * This test ensures that selecting the 'Extra' pool name updates the exam
     * element field with the correct value.
     *
     * Asserts:
     * - Selecting 'Extra' updates the exam element field to '4'.
     */
    test('UT-136: pool name selection updates exam element to 4 for Extra', () => {
        const poolNameDropdown = document.getElementById('pool-name');
        const examElementField = document.getElementById('exam-element');

        poolNameDropdown.value = 'Extra';
        const changeEvent = new Event('change');
        poolNameDropdown.dispatchEvent(changeEvent);

        expect(examElementField.value).toBe('4');
    });
    
    /**
     * Test ID: UT-137
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
    test('UT-137: submit pool form handles non-OK response', async () => {
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
     * Test ID: UT-150
     * Test the functionality of clicking a pool row to add the "show" class if the expandable row is hidden.
     *
     * This test ensures that when a pool row is clicked and the expandable row is initially hidden,
     * the "show" class is added to make it visible.
     *
     * Asserts:
     * - Clicking a pool row adds the "show" class to the expandable row when it is hidden.
     */
    test('UT-150: clicking a pool row adds "show" class if expandable row is hidden', async () => {
        // Initially, the expandable row should not have the "show" class
        expect(expandableRow.classList.contains('show')).toBe(false);
    
        // Simulate clicking the pool row
        poolRow.click();
    
        // Wait for any asynchronous code to complete
        await Promise.resolve();
    
        // Now, check if the "show" class has been added
        expect(expandableRow.classList.contains('show')).toBe(true);
    });
    
    /**
     * Test ID: UT-151
     * Test the functionality of clicking a pool row to remove the "show" class if the expandable row is shown.
     *
     * This test ensures that when a pool row is clicked and the expandable row is initially shown,
     * the "show" class is removed to hide it.
     *
     * Asserts:
     * - Clicking a pool row removes the "show" class from the expandable row when it is visible.
     */
    test('UT-151: clicking a pool row removes "show" class if expandable row is shown', () => {
        // Add the "show" class initially
        expandableRow.classList.add('show');
        expect(expandableRow.classList.contains('show')).toBe(true);

        // Click the pool row
        poolRow.click();

        // The "show" class should now be removed
        expect(expandableRow.classList.contains('show')).toBe(false);
    });

    /**
     * Test ID: UT-152
     * Test the functionality of clicking a pool row when no corresponding expandable row is found.
     *
     * This test ensures that when a pool row is clicked, but no expandable row with the matching data-id exists,
     * an error is logged to the console.
     *
     * Asserts:
     * - If no expandable row exists, an error is logged with the correct message.
     */
    test('UT-152: clicking a pool row logs an error if no expandable row is found', () => {
        // Remove the expandable row from the DOM
        expandableRow.remove();

        // Click the pool row
        poolRow.click();

        // Ensure console.error is called with the correct message
        expect(console.error).toHaveBeenCalledWith('No expandable row found for pool ID: 1');
    });

    /**
     * Test ID: UT-153
     * Test the functionality of clicking the upload button to show the modal.
     *
     * This test ensures that clicking the "Upload" button opens the corresponding modal.
     *
     * Asserts:
     * - Clicking the "Upload" button adds the "is-active" class to the modal.
     */
    test('UT-153: clicking the upload button shows the corresponding modal', () => {
        // Simulate clicking the upload button
        const uploadButton = document.getElementById('upload-button-2');
        const modal = document.getElementById('upload-modal-2');
    
        // Initially, the modal should not be active
        expect(modal.classList.contains('is-active')).toBe(false);
    
        uploadButton.click();
    
        // Assert that the modal becomes active (is shown)
        expect(modal.classList.contains('is-active')).toBe(true);
    });

    /**
     * Test ID: UT-154
     * Test the functionality of clicking on a thumbnail image to show the fullscreen overlay.
     *
     * This test ensures that clicking the thumbnail image sets the fullscreen image src
     * and makes the fullscreen overlay visible.
     *
     * Asserts:
     * - The fullscreen overlay becomes visible when clicking the thumbnail image.
     * - The fullscreen image's source is correctly set to the thumbnail image's source.
     */
    test('UT-154: clicking thumbnail image shows fullscreen overlay', () => {
        // Reference the thumbnail image and fullscreen elements
        const thumbnailImage = document.querySelector('.thumbnail-image');
        const fullscreenOverlay = document.getElementById('fullscreen-overlay');
        const fullscreenImage = document.getElementById('fullscreen-image');

        // Simulate clicking the thumbnail image
        thumbnailImage.click();

        // Assert that the fullscreen image source is set correctly
        expect(fullscreenImage.src).toContain('http://localhost/static/images/diagrams/1_T1.jpg');

        // Assert that the fullscreen overlay becomes visible
        expect(fullscreenOverlay.style.display).toBe('flex');
    });

    /**
     * Test ID: UT-155
     * Test the functionality of clicking the fullscreen overlay to hide it.
     *
     * This test ensures that clicking the fullscreen overlay hides it from view.
     *
     * Asserts:
     * - The fullscreen overlay becomes hidden after clicking it.
     */
    test('UT-155: clicking fullscreen overlay hides it', () => {
        // Reference the fullscreen overlay element
        const fullscreenOverlay = document.getElementById('fullscreen-overlay');

        // Simulate opening the fullscreen overlay by setting its display to 'flex'
        fullscreenOverlay.style.display = 'flex';

        // Ensure the overlay is initially visible
        expect(fullscreenOverlay.style.display).toBe('flex');

        // Simulate clicking the fullscreen overlay to close it
        fullscreenOverlay.click();

        // Assert that the overlay is hidden after clicking
        expect(fullscreenOverlay.style.display).toBe('none');
    });
    
    /**
     * Test ID: UT-156
     * Test the functionality of clicking the "Upload" button to open the upload modal.
     *
     * This test ensures that clicking the "Upload" button opens the corresponding modal.
     *
     * Asserts:
     * - Clicking the "Upload" button adds the "is-active" class to the modal.
     */
    test('UT-156: Open upload modal when "Upload" button is clicked', () => {
        // Reference the upload button and the modal elements
        const uploadButton = document.querySelector('.upload-diagram-button');
        const modal = document.getElementById('upload-modal-1');

        // Simulate clicking the upload button
        uploadButton.click();

        // Assert that the modal becomes active (is shown)
        expect(modal.classList.contains('is-active')).toBe(true);
    });

    /**
     * Test ID: UT-157
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
    test('UT-157: Handle upload submission and close modal upon successful response', async () => {
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
});
