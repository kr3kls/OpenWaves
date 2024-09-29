/**
 * File: pools.test.js
 * 
 * Description: This file contains tests for the pools page functionality.
 * 
 * @jest-environment jsdom
 */

require('../openwaves/static/js/pools'); // This will execute the pools.js code, including the DOMContentLoaded event

describe('Pool management functionality', () => {
    let csrfTokenInput;

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
        <input name="csrf_token" value="dummy-csrf-token" />
        <button id="create-pool-button"></button>  <!-- Mock the create pool button -->
        <form id="create-pool-form">
            <!-- Form inputs... -->
            <button id="submit-pool-form"></button>  <!-- Mock submit button -->
        </form>
        <div id="create-pool-modal" class="modal"></div>  <!-- Mock modal -->
        <button class="delete-pool-button" data-id="1" data-name="Test Pool"></button>
        <button id="upload-button-1"></button>  <!-- Mock upload button -->
        <div id="upload-modal-1" class="modal">
            <button class="delete"></button>  <!-- Mock close button -->
            <button id="cancel-pool-form"></button>  <!-- Mock cancel button -->
            <button id="submit-upload-1"></button>  <!-- Mock submit button -->
        </div>  <!-- Mock upload modal -->
        <input id="start-date" type="date" />
        <input id="end-date" type="date" />
        <select id="pool-name">
            <option value="Technician">Technician</option>
            <option value="General">General</option>
            <option value="Extra">Extra</option>
        </select>
        <input id="exam-element" />
    `;
    
        csrfTokenInput = document.querySelector('input[name="csrf_token"]');
        
        // Mock window.confirm and window.alert to prevent actual prompts during tests
        jest.spyOn(window, 'confirm').mockImplementation(() => true);
        jest.spyOn(window, 'alert').mockImplementation(() => {});
        jest.spyOn(console, 'error').mockImplementation(() => {});
    
        // Mock fetch API
        global.fetch = jest.fn(() => Promise.resolve({ ok: true }));
    
        // Simulate DOMContentLoaded to initialize event listeners
        document.dispatchEvent(new Event('DOMContentLoaded'));

        consoleErrorMock = jest.spyOn(console, 'error').mockImplementation(() => {});
    });
    

    afterEach(() => {
        jest.clearAllMocks();
        consoleErrorMock.mockRestore();
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
     * Test ID: UT-125
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
     * Test ID: UT-126
     * Test the functionality of the upload button triggering modal visibility.
     *
     * This test ensures that clicking the upload button opens the corresponding modal, 
     * allowing users to interact with the upload form.
     *
     * Asserts:
     * - The modal becomes active (is shown) after clicking the upload button.
     */
    test('upload button triggers modal visibility', () => {
        const uploadButton = document.getElementById('upload-button-1');
        const modal = document.getElementById('upload-modal-1');
        
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
    test('submit upload form handles non-OK response', async () => {
        const modal = document.getElementById('upload-modal-1');
        const submitButton = document.getElementById('submit-upload-1');
        
        const form = document.createElement('form');
        form.setAttribute('id', 'upload-form-1');
        document.body.appendChild(form);
        const formData = new FormData(form);
    
        // Mock fetch to return ok: false
        global.fetch = jest.fn(() => Promise.resolve({ ok: false }));
    
        // Simulate form submission
        submitButton.click();
        await Promise.resolve();
    
        expect(fetch).toHaveBeenCalledWith('/ve/upload_questions/1', {
            method: 'POST',
            body: formData,
        });
    
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
    test('submit upload form triggers fetch and closes modal', async () => {
        const modal = document.getElementById('upload-modal-1');
        const submitButton = document.getElementById('submit-upload-1');
        
        const form = document.createElement('form');
        form.setAttribute('id', 'upload-form-1');
        document.body.appendChild(form);
        const formData = new FormData(form);

        global.fetch = jest.fn(() => Promise.resolve({ ok: true }));

        // Simulate form submission
        submitButton.click();
        await Promise.resolve();

        expect(fetch).toHaveBeenCalledWith('/ve/upload_questions/1', {
            method: 'POST',
            body: formData,
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
    test('close modal when cancel is clicked', () => {
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
    test('close modal when X is clicked', () => {
        // Get the close button (X) and the modal from the DOM
        const closeButton = document.querySelector('.delete'); // X button class
        const modal = document.getElementById('create-pool-modal');
    
        // Ensure the modal starts as active (open)
        modal.classList.add('is-active'); // This opens the modal
    
        // Ensure the modal is actually open before closing
        expect(modal.classList.contains('is-active')).toBe(true);
    
        // Try to close with the close button
        closeButton.click(); 
    
        // Assert the modal is no longer active (closed)
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
     */
    test('submit pool form triggers fetch and closes modal', async () => {
        const modal = document.getElementById('create-pool-modal');
        const createPoolForm = document.getElementById('create-pool-form');
        const submitPoolFormButton = document.getElementById('submit-pool-form');

        modal.classList.add('is-active');

        global.fetch = jest.fn(() =>
            Promise.resolve({
                json: () => Promise.resolve({ success: true }),
            })
        );

        submitPoolFormButton.click();
        await Promise.resolve();

        expect(fetch).toHaveBeenCalledWith('/ve/create_pool', expect.any(Object));

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
    test('start date change updates end date automatically', () => {
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
    test('create pool button sets default dates and opens modal', () => {
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
    test('pool name selection updates exam element to 2 for Technician', () => {
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
    test('pool name selection updates exam element to 3 for General', () => {
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
    test('pool name selection updates exam element to 4 for Extra', () => {
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
});
