/**
 * File: makeRequest.test.js
 *
 * Description: This file contains tests for the makeRequest functionality.
 *
 * @jest-environment jsdom
 */

const { makeRequest } = require('../openwaves/static/js/ve_sessions');

describe('makeRequest', () => {
    let consoleErrorMock;

    beforeEach(() => {
        // Mock fetch globally to simulate network requests
        global.fetch = jest.fn();

        // Mock console.error to suppress output during tests
        consoleErrorMock = jest.spyOn(console, 'error').mockImplementation(() => {});

        // Mock window.location.reload to prevent navigation errors in jsdom
        Object.defineProperty(window, 'location', {
            writable: true,
            value: { reload: jest.fn() }, // Mock reload method
        });

        // Mock window.alert
        jest.spyOn(window, 'alert').mockImplementation(() => {});

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

        // Simulate DOMContentLoaded event
        document.dispatchEvent(new Event('DOMContentLoaded'));
    });

    afterEach(() => {
        // Restore console.error after each test to avoid side effects
        consoleErrorMock.mockRestore();

        // Clear all fetch mocks
        jest.clearAllMocks();
    });

    it('should handle fetch errors in makeRequest', async () => {
        // Mock fetch to reject
        fetch.mockRejectedValueOnce(new Error('Network error'));
    
        const closeButton = document.querySelector('.close-session-button');
        
        // Check if closeButton exists before clicking
        if (closeButton) {
            closeButton.click();
        } else {
            throw new Error('close-session-button element not found in the DOM');
        }
    
        await new Promise((resolve) => setTimeout(resolve, 0));
    
        expect(window.alert).toHaveBeenCalledWith('An error occurred. Please try again.');
    });
    

    it('should throw an error if the server responds with a non-OK status', async () => {
        // Mock fetch to return a response with status 500
        fetch.mockResolvedValueOnce({
            ok: false,
            status: 500,  // Simulate a server error status
            json: () => Promise.resolve({}),
        });

        // Use try-catch to handle the error thrown by makeRequest
        try {
            await makeRequest('/ve/create_session', 'POST');
            // If no error is thrown, fail the test
            throw new Error('makeRequest did not throw an error for non-OK response');
        } catch (error) {
            // Assert that the error message matches the expected error thrown
            expect(error.message).toBe('Server responded with status: 500');
        }

        // Ensure fetch was called with the correct parameters
        expect(fetch).toHaveBeenCalledWith('/ve/create_session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: null,
        });
    });
});
