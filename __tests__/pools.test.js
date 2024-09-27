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
        </select>
        <input id="exam-element" />
    `;
    
        csrfTokenInput = document.querySelector('input[name="csrf_token"]');
        
        // Mock window.confirm and window.alert to prevent actual prompts during tests
        jest.spyOn(window, 'confirm').mockImplementation(() => true);
        jest.spyOn(window, 'alert').mockImplementation(() => {});
    
        // Mock fetch API
        global.fetch = jest.fn(() => Promise.resolve({ ok: true }));
    
        // Simulate DOMContentLoaded to initialize event listeners
        document.dispatchEvent(new Event('DOMContentLoaded'));
    });
    

    afterEach(() => {
        jest.clearAllMocks();
    });


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


    test('delete pool button triggers error alert on fetch failure', async () => {
        global.fetch = jest.fn(() => Promise.resolve({ ok: false }));  // Mock a failure response
        const deleteButton = document.querySelector('.delete-pool-button');
        deleteButton.click();
        await Promise.resolve();

        expect(window.alert).toHaveBeenCalledWith('There was an error deleting the pool.');
    });


    test('upload button triggers modal visibility', () => {
        const uploadButton = document.getElementById('upload-button-1');
        const modal = document.getElementById('upload-modal-1');
        
        // Simulate clicking the upload button
        uploadButton.click();
        
        // Assert the modal becomes active
        expect(modal.classList.contains('is-active')).toBe(true);
    });


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


    test('pool name selection updates exam element', () => {
        const poolNameDropdown = document.getElementById('pool-name');
        const examElementField = document.getElementById('exam-element');

        poolNameDropdown.value = 'General';
        const changeEvent = new Event('change');
        poolNameDropdown.dispatchEvent(changeEvent);

        expect(examElementField.value).toBe('3');
    });


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
});
