/**
 * File: ve_results.test.js
 * 
 * Description: This file contains tests for the ve_results functionality.
 * 
 * @jest-environment jsdom
 */

// Mock the DOMContentLoaded event
document.addEventListener = jest.fn((event, callback) => {
    if (event === 'DOMContentLoaded') {
        callback(); // Simulate DOMContentLoaded event
    }
});

describe('ve_results functionality', () => {
    let csrfTokenInput;

    beforeEach(() => {
        // Set up the HTML structure with necessary elements for the test
        document.body.innerHTML = `
            <input type="hidden" name="csrf_token" value="dummy-csrf-token" />
            <table>
                <tr class="clickable-row" data-session-id="13" data-exam-element="2" data-hc-id="1">
                    <td>Row Data</td>
                </tr>
            </table>
        `;

        // Get the CSRF token element
        csrfTokenInput = document.querySelector('input[name="csrf_token"]');

        // Spy on form submission to prevent actual form submission
        HTMLFormElement.prototype.submit = jest.fn();
        
        // Import the JavaScript file containing the code to test
        require('../openwaves/static/js/ve_results.js');

        // Trigger DOMContentLoaded event to attach event listeners
        document.dispatchEvent(new Event('DOMContentLoaded'));
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    /**
     * Test ID: UT-258
     * Test creating and submitting a form with the correct data when a row is clicked.
     *
     * This test ensures that clicking a row with the class 'clickable-row' creates and
     * submits a form populated with the correct session data.
     *
     * Asserts:
     * - A form is created and its method is set to 'post'.
     * - The form's action URL ends with '/ve/exam/results'.
     * - Hidden input fields for 'session_id', 'exam_element', 'hc_id', and 'csrf_token'
     *   are created and contain the expected values.
     * - The form's `submit` method is called to initiate submission.
     */
    it('should create and submit a form with the correct data when a row is clicked', () => {
        // Simulate a click on the .clickable-row
        const row = document.querySelector('.clickable-row');
        row.click();

        // Find the form that was created
        const form = document.querySelector('form');
        expect(form).not.toBeNull(); // Ensure the form was created
        expect(form.method).toBe('post');
        expect(form.action).toMatch(/\/ve\/exam\/results$/);

        // Check that hidden inputs are created and have correct values
        const sessionInput = form.querySelector('input[name="session_id"]');
        const elementInput = form.querySelector('input[name="exam_element"]');
        const hcInput = form.querySelector('input[name="hc_id"]');
        const csrfInput = form.querySelector('input[name="csrf_token"]');

        expect(sessionInput).not.toBeNull();
        expect(sessionInput.value).toBe('13');
        expect(elementInput).not.toBeNull();
        expect(elementInput.value).toBe('2');
        expect(hcInput).not.toBeNull();
        expect(hcInput.value).toBe('1');
        
        expect(csrfInput).not.toBeNull();
        expect(csrfInput.value).toBe(csrfTokenInput.value);

        // Verify that form.submit was called
        expect(HTMLFormElement.prototype.submit).toHaveBeenCalled();
    });
});
