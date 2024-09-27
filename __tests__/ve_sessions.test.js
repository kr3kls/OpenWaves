/**
 * File: ve_sessions.test.js
 * 
 * Description: This file contains tests for the ve_sessions page functionality.
 * 
 * @jest-environment jsdom
 */

require('../openwaves/static/js/ve_sessions'); // This will execute the ve_sessions.js code, including the DOMContentLoaded event

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

    beforeEach(() => {
        // Mock window.location.reload to prevent navigation errors in jsdom
        Object.defineProperty(window, 'location', {
            writable: true,
            value: { reload: jest.fn() }, // Mock reload method
        });

        // Set up a minimal DOM structure needed for tests
        document.body.innerHTML = `
            <input name="csrf_token" value="dummy-csrf-token" />
            <button id="create-session-button"></button>
            <div id="create-session-modal" class="modal"></div>
            <button id="submit-session-form"></button>
            <form id="create-session-form"></form>
            <button class="delete-session-button" data-id="1"></button>
            <button class="open-session-button" data-id="2"></button>
            <button class="close-session-button" data-id="3"></button>
            <input id="start-date" />
        `;

        createSessionButton = document.getElementById('create-session-button');
        createSessionModal = document.getElementById('create-session-modal');
        submitSessionForm = document.getElementById('submit-session-form');
        createSessionForm = document.getElementById('create-session-form');
        csrfTokenInput = document.querySelector('input[name="csrf_token"]');

        // Mock fetch API
        global.fetch = jest.fn(() => Promise.resolve({
            ok: true, 
            json: () => Promise.resolve({ success: true }) // Mock success response
        }));

        // Simulate DOMContentLoaded event
        document.dispatchEvent(new Event('DOMContentLoaded'));
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    it('should set today\'s date as default in the start date field', () => {
        const startDateField = document.getElementById('start-date');
        const today = new Date().toISOString().split('T')[0];
        expect(startDateField.value).toBe(today);
    });

    it('should open the session modal when the create session button is clicked', () => {
        createSessionButton.click();
        expect(createSessionModal.classList.contains('is-active')).toBe(true);
    });

    it('should submit the session form and handle success response', async () => {
        // Simulate form submission
        submitSessionForm.click();

        // Use setTimeout to wait for promise resolution
        await new Promise(resolve => setTimeout(resolve, 0));

        // Assert that fetch was called with the correct URL and options
        expect(fetch).toHaveBeenCalledWith('/ve/create_session', expect.any(Object));

        // Assert that fetch was called exactly once
        expect(fetch).toHaveBeenCalledTimes(1);

        // Assert that location.reload was called
        expect(window.location.reload).toHaveBeenCalled();
    });

    it('should call fetch with the correct parameters for delete session', () => {
        const deleteButton = document.querySelector('.delete-session-button');
        window.confirm = jest.fn(() => true); // Mock confirm dialog to always return true
        deleteButton.click();

        expect(fetch).toHaveBeenCalledWith('/ve/delete_session/1', expect.any(Object));
    });

    it('should not call fetch when deleting a session if confirm is denied', () => {
        const deleteButton = document.querySelector('.delete-session-button');
        window.confirm = jest.fn(() => false); // Mock confirm dialog to return false
        deleteButton.click();

        expect(fetch).not.toHaveBeenCalled();
    });

    it('should call fetch with the correct parameters for opening a session', () => {
        const openButton = document.querySelector('.open-session-button');
        openButton.click();

        expect(fetch).toHaveBeenCalledWith('/ve/open_session/2', expect.any(Object));
    });

    it('should call fetch with the correct parameters for closing a session', () => {
        const closeButton = document.querySelector('.close-session-button');
        closeButton.click();

        expect(fetch).toHaveBeenCalledWith('/ve/close_session/3', expect.any(Object));
    });
});
