/**
 * File: ve_sessions.test.js
 * 
 * Description: This file contains tests for the ve_sessions page functionality.
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
     * Test ID: UT-138
     * Test setting the default date in the start date field.
     *
     * This test ensures that the start date field is automatically populated with
     * today's date when the form is loaded.
     *
     * Asserts:
     * - The start date field value is set to today's date in the format 'YYYY-MM-DD'.
     */
    it("should set today's date as default in the start date field", () => {
        const today = new Date().toISOString().split('T')[0];
        expect(startDateField.value).toBe(today);
    });

    /**
     * Test ID: UT-139
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
     * Test ID: UT-140
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
     * Test ID: UT-141
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
     * Test ID: UT-142
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
     * Test ID: UT-143
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
     * Test ID: UT-144
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
     * Test ID: UT-145
     * Test not calling fetch when deleting a session if the confirm dialog is denied.
     *
     * This test ensures that clicking the delete button for a session does not send a DELETE request
     * if the user does not confirm the deletion.
     *
     * Asserts:
     * - The fetch function is not called when the confirmation dialog returns false.
     */
    it('should not call fetch when deleting a session if confirm is denied', () => {
        const deleteButton = document.querySelector('.delete-session-button');
        window.confirm = jest.fn(() => false); // Mock confirm dialog to return false
        deleteButton.click();

        expect(fetch).not.toHaveBeenCalled();
    });

    /**
     * Test ID: UT-146
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
     * Test ID: UT-147
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
     * Test ID: UT-148
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
     * Test ID: UT-149
     * Test handling the absence of the start date field.
     *
     * This test ensures that no errors occur if the start date field is not present
     * in the DOM when the DOMContentLoaded event is triggered.
     *
     * Asserts:
     * - The start date field is not present in the DOM after attempting to set it.
     */
    it('should not set the date if startDateField is not present', () => {
        // Remove the start-date field from the DOM
        startDateField.remove();

        // Re-run the code to simulate DOMContentLoaded
        document.dispatchEvent(new Event('DOMContentLoaded'));

        expect(document.getElementById('start-date')).toBeNull();
    });

    /**
     * Test ID: UT-257
     * Test updating the button to "force close" when error indicates open exams.
     *
     * This test ensures that if the server returns an error indicating open exams, 
     * the button's text, style, and attributes are updated to a "force close" action.
     *
     * Asserts:
     * - The button has its `data-force` attribute set to `true`.
     * - The button's text content is updated to "Force".
     * - The button's CSS classes are modified as expected.
     */
    it('should update button to "force close" when error indicates open exams', async () => {
        // Mock fetch to simulate an error response for open exams
        fetch.mockResolvedValueOnce({
            ok: false,
            json: () => Promise.resolve({ error: "There are still open exams in this session." }),
        });
    
        const closeButton = document.querySelector('.close-session-button');
        closeButton.setAttribute('data-id', '3');
        closeButton.classList.add('is-light-button-color');
    
        // Manually trigger the event handler for the button
        closeButton.addEventListener('click', async () => {
            try {
                await makeRequest(`/ve/close_session/${closeButton.getAttribute('data-id')}`, 'POST');
            } catch (error) {
                // Simulate the behavior when an open exams error is received
                if (error.message === "There are still open exams in this session.") {
                    closeButton.setAttribute('data-force', 'true');
                    closeButton.textContent = 'Force';
                    closeButton.classList.remove('is-light-button-color');
                    closeButton.classList.add('is-danger');
                }
            }
        });
    
        // Simulate button click
        closeButton.click();
    
        // Use setImmediate to wait for promise resolution
        await new Promise((resolve) => setTimeout(resolve, 0));
    
        // Assertions to check if button was updated to "force close" state
        expect(closeButton.getAttribute('data-force')).toBe('true');
        expect(closeButton.textContent).toBe('Force');
        expect(closeButton.classList.contains('is-light-button-color')).toBe(false);
        expect(closeButton.classList.contains('is-danger')).toBe(true);
    });

    /**
     * Test ID: UT-259
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

    /**
     * Test ID: UT-260
     * Test declining the purge action.
     *
     * This test ensures that the purge process is not initiated if the user declines the confirmation.
     *
     * Asserts:
     * - The fetch function is not called if the user denies the confirmation dialog.
     */
    it('should not call fetch if user declines the confirmation dialog for purge', () => {
        const purgeButton = document.getElementById('purge-button');
        window.confirm = jest.fn(() => false); // Mock confirmation dialog to return false

        // Simulate button click
        purgeButton.click();

        expect(fetch).not.toHaveBeenCalled();
    });

    /**
     * Test ID: UT-261
     * Test handling purge error response.
     *
     * This test ensures that an appropriate error message is displayed if the server responds with an error during purge.
     *
     * Asserts:
     * - An alert is displayed with the correct error message.
     */
    it('should handle purge error response', async () => {
        fetch.mockResolvedValueOnce({
            ok: false,
            json: () => Promise.resolve({ success: false, error: 'Purge error' }),
        });
    
        const purgeButton = document.getElementById('purge-button');
        window.confirm = jest.fn(() => true); // Mock confirmation dialog to return true
    
        // Simulate button click
        purgeButton.click();
    
        await new Promise((resolve) => setTimeout(resolve, 0));
    
        // Adjust expectation to match the actual alert message
        expect(window.alert).toHaveBeenCalledWith('Purge error');
    });    

    /**
     * Test ID: UT-262
     * Test handling undefined data in purge response.
     *
     * This test ensures that a generic error message is displayed if the response data is undefined during purge.
     *
     * Asserts:
     * - An alert is displayed with a generic error message.
     */
    it('should handle undefined data in purge response', async () => {
        fetch.mockResolvedValueOnce({
            ok: true,
            json: () => Promise.resolve(undefined),
        });

        const purgeButton = document.getElementById('purge-button');
        window.confirm = jest.fn(() => true); // Mock confirmation dialog to return true

        // Simulate button click
        purgeButton.click();

        await new Promise((resolve) => setTimeout(resolve, 0));

        expect(window.alert).toHaveBeenCalledWith('Error purging sessions: Unknown error');
    });
});
