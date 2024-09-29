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

    it("should set today's date as default in the start date field", () => {
        const today = new Date().toISOString().split('T')[0];
        expect(startDateField.value).toBe(today);
    });

    it('should open the session modal when the create session button is clicked', () => {
        createSessionButton.click();
        expect(createSessionModal.classList.contains('is-active')).toBe(true);
    });

    it('should close the session modal when a close element is clicked', () => {
        const modal = document.querySelector('.modal');
        const closeButton = modal.querySelector('.delete');

        // Open the modal first
        modal.classList.add('is-active');

        // Simulate click on the close button
        closeButton.click();

        expect(modal.classList.contains('is-active')).toBe(false);
    });

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

    it('should not call fetch when deleting a session if confirm is denied', () => {
        const deleteButton = document.querySelector('.delete-session-button');
        window.confirm = jest.fn(() => false); // Mock confirm dialog to return false
        deleteButton.click();

        expect(fetch).not.toHaveBeenCalled();
    });

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

    it('should not set the date if startDateField is not present', () => {
        // Remove the start-date field from the DOM
        startDateField.remove();

        // Re-run the code to simulate DOMContentLoaded
        document.dispatchEvent(new Event('DOMContentLoaded'));

        expect(document.getElementById('start-date')).toBeNull();
    });

    it('should not throw an error if csrfToken is not present', async () => {
        // Remove the csrf_token input
        csrfTokenInput.remove();

        const closeButton = document.querySelector('.close-session-button');
        closeButton.click();

        await new Promise((resolve) => setTimeout(resolve, 0));

        // The fetch should still have been called without the CSRF token
        expect(fetch).toHaveBeenCalledWith('/ve/close_session/3', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ action: 'close' }),
        });
    });
});
