/**
 * File: ve_sessions.test.js
 * 
 * Description: This file contains integration tests for the ve_sessions page functionality.
 * 
 * @jest-environment jsdom
 */

// Import the module that contains the code to be tested
require('../openwaves/static/js/ve_sessions');
const { makeRequest } = require('../openwaves/static/js/ve_sessions');


// Mock the DOMContentLoaded event
document.addEventListener = jest.fn((event, callback) => {
    if (event === 'DOMContentLoaded') {
        callback(); // Simulate DOMContentLoaded event
    }
});

describe('Modal and session handling', () => {
    let createSessionButton;
    let createSessionModal;
    let submitSessionForm;
    let createSessionForm;
    let csrfTokenInput;
    let startDateField;

    beforeEach(() => {
        // Mock window.location.reload to prevent navigation errors in jsdom
        Object.defineProperty(window, 'location', {
            writable: true,
            value: { reload: jest.fn() }, // Mock reload method
        });

        // Mock window.alert
        jest.spyOn(window, 'alert').mockImplementation(() => {});

        // Suppress console.error to prevent clutter during test execution
        consoleErrorMock = jest.spyOn(console, 'error').mockImplementation(() => {});

        // Set up a minimal DOM structure needed for tests
        document.body.innerHTML = `
            <input name="csrf_token" value="dummy-csrf-token" />
            <button id="create-session-button"></button>
            <div id="create-session-modal" class="modal">
            <button class="delete"></button></div>
            <button id="submit-session-form"></button>
            <form id="create-session-form"></form>
            <button class="delete-session-button" data-id="1"></button>
            <button class="open-session-button" data-id="2"></button>
            <button class="close-session-button" data-id="3"></button>
            <input id="start-date" />
            <div class="is-flex is-justify-content-flex-start is-relative mt-4">
                <button class="button is-danger" id="purge-button">Purge</button>
            </div>
            <div class="modal">
                <button class="delete"></button>
                <button class="button is-light-button-color"></button>
                <div class="modal-background"></div>
            </div>
        `;

        createSessionButton = document.getElementById('create-session-button');
        createSessionModal = document.getElementById('create-session-modal');
        submitSessionForm = document.getElementById('submit-session-form');
        createSessionForm = document.getElementById('create-session-form');
        csrfTokenInput = document.querySelector('input[name="csrf_token"]');
        startDateField = document.getElementById('start-date');

        // Mock fetch API
        global.fetch = jest.fn(() =>
            Promise.resolve({
                ok: true,
                json: () => Promise.resolve({ success: true }), // Mock success response
            })
        );

        // Simulate DOMContentLoaded event
        document.dispatchEvent(new Event('DOMContentLoaded'));
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    /**
     * Test ID: IT-163
     * Test opening the session modal when the create session button is clicked.
     *
     * This test ensures that clicking the 'create session' button properly opens
     * the session creation modal.
     *
     * Asserts:
     * - The session modal contains the 'is-active' class when the button is clicked.
     */
    it('should open the session modal when the create session button is clicked', () => {
        createSessionButton.click();
        expect(createSessionModal.classList.contains('is-active')).toBe(true);
    });

    /**
     * Test ID: IT-164
     * Test closing the session modal when a close element is clicked.
     *
     * This test ensures that clicking a close element in the session modal properly
     * closes the modal.
     *
     * Asserts:
     * - The modal is open before the close button is clicked.
     * - The modal no longer contains the 'is-active' class after the close button is clicked.
     */
    it('should close the session modal when a close element is clicked', () => {
        const modal = document.querySelector('.modal');
        const closeButton = modal.querySelector('.delete');

        // Open the modal first
        modal.classList.add('is-active');

        // Simulate click on the close button
        closeButton.click();

        expect(modal.classList.contains('is-active')).toBe(false);
    });

    /**
     * Test ID: IT-165
     * Test submitting the session form and handling a successful response.
     *
     * This test ensures that clicking the submit button properly sends a request to create a session
     * and reloads the page when the request is successful.
     *
     * Asserts:
     * - The fetch function is called with the correct URL and options.
     * - The window.location.reload function is called after a successful response.
     */
    it('should submit the session form and handle success response', async () => {
        // Simulate form submission
        submitSessionForm.click();

        // Use setImmediate to wait for promise resolution
        await new Promise((resolve) => setTimeout(resolve, 0));

        // Assert that fetch was called with the correct URL and options
        expect(fetch).toHaveBeenCalledWith('/ve/create_session', {
            method: 'POST',
            body: expect.any(FormData),
        });

        // Assert that location.reload was called
        expect(window.location.reload).toHaveBeenCalled();
    });

    /**
     * Test ID: IT-166
     * Test handling form submission error response.
     *
     * This test ensures that the appropriate error message is displayed when the server responds
     * with a non-OK status code during session form submission.
     *
     * Asserts:
     * - The window.alert function is called with the correct error message from the response.
     */
    it('should handle form submission error response', async () => {
        // Mock fetch to return a failure response with status 400 and an error message
        fetch.mockResolvedValueOnce({
            ok: false,
            json: () => Promise.resolve({ success: false, error: 'Test error' }),
        });
    
        // Simulate form submission
        submitSessionForm.click();
    
        await new Promise((resolve) => setTimeout(resolve, 0));
    
        // Update the expectation to match the actual alert message
        expect(window.alert).toHaveBeenCalledWith('Test error');
    });     

    /**
     * Test ID: IT-167
     * Test handling undefined data response in session form submission.
     *
     * This test ensures that an appropriate error message is displayed when the server returns an
     * undefined response during session form submission.
     *
     * Asserts:
     * - The window.alert function is called with a generic error message if the response data is undefined.
     */
    it('should handle undefined data response in session form submission', async () => {
        // Mock fetch to return undefined data
        fetch.mockResolvedValueOnce({
            ok: true,
            json: () => Promise.resolve(undefined),
        });
    
        // Simulate form submission
        submitSessionForm.click();
    
        await new Promise((resolve) => setTimeout(resolve, 0));
    
        // Check that an alert is displayed with a generic error message
        expect(window.alert).toHaveBeenCalledWith('Error creating session: Unknown error');
    });
    
    /**
     * Test ID: IT-168
     * Test deleting a session by calling fetch with the correct parameters.
     *
     * This test ensures that clicking the delete button for a session sends a DELETE request
     * with the appropriate parameters if the user confirms the deletion.
     *
     * Asserts:
     * - The fetch function is called with the correct URL, method, headers, and body.
     */
    it('should call fetch with the correct parameters for delete session', async () => {
        const deleteButton = document.querySelector('.delete-session-button');
        window.confirm = jest.fn(() => true); // Mock confirm dialog to always return true
        deleteButton.click();

        await new Promise((resolve) => setTimeout(resolve, 0));

        expect(fetch).toHaveBeenCalledWith('/ve/delete_session/1', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': 'dummy-csrf-token',
            },
            body: JSON.stringify({ action: 'delete' }),
        });
    });

    /**
     * Test ID: IT-169
     * Test opening a session by calling fetch with the correct parameters.
     *
     * This test ensures that clicking the open button for a session sends a POST request
     * with the appropriate parameters to open the session.
     *
     * Asserts:
     * - The fetch function is called with the correct URL, method, headers, and body.
     */
    it('should call fetch with the correct parameters for opening a session', async () => {
        const openButton = document.querySelector('.open-session-button');
        openButton.click();

        await new Promise((resolve) => setTimeout(resolve, 0));

        expect(fetch).toHaveBeenCalledWith('/ve/open_session/2', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': 'dummy-csrf-token',
            },
            body: JSON.stringify({ action: 'open' }),
        });
    });

    /**
     * Test ID: IT-170
     * Test closing a session by calling fetch with the correct parameters.
     *
     * This test ensures that clicking the close button for a session sends a POST request
     * with the appropriate parameters to close the session.
     *
     * Asserts:
     * - The fetch function is called with the correct URL, method, headers, and body.
     */
    it('should call fetch with the correct parameters for closing a session', async () => {
        const closeButton = document.querySelector('.close-session-button');
        closeButton.click();

        await new Promise((resolve) => setTimeout(resolve, 0));

        expect(fetch).toHaveBeenCalledWith('/ve/close_session/3', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': 'dummy-csrf-token',
            },
            body: JSON.stringify({ action: 'close' }),
        });
    });

    /**
     * Test ID: IT-171
     * Test handling unsuccessful responses in session actions.
     *
     * This test ensures that an appropriate error message is displayed when a session action,
     * such as opening a session, fails due to an unsuccessful response from the server.
     *
     * Asserts:
     * - An alert is displayed with the appropriate error message when the response is unsuccessful.
     */
    it('should handle unsuccessful responses in session actions', async () => {
        fetch.mockResolvedValueOnce({
            ok: true,
            json: () => Promise.resolve({ success: false, error: 'Session error' }),
        });

        const openButton = document.querySelector('.open-session-button');
        openButton.click();

        await new Promise((resolve) => setTimeout(resolve, 0));

        expect(window.alert).toHaveBeenCalledWith('Error open session: Session error');
    });

    /**
     * Test ID: IT-172
     * Test confirming the purge action.
     *
     * This test ensures that the purge process proceeds if the user confirms the action.
     *
     * Asserts:
     * - The fetch function is called with the correct URL, method, and headers.
     * - The window.location.reload function is called after a successful response.
     */
    it('should confirm and call fetch to purge sessions if user confirms', async () => {
        const purgeButton = document.getElementById('purge-button');
        window.confirm = jest.fn(() => true); // Mock confirmation dialog to return true
    
        // Simulate button click
        purgeButton.click();
    
        await new Promise((resolve) => setTimeout(resolve, 0));
    
        expect(fetch).toHaveBeenCalledWith('/ve/purge_sessions', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': 'dummy-csrf-token',
            },
            body: null, // Include body: null here to match the actual call
        });
        expect(window.location.reload).toHaveBeenCalled();
    });    
});
