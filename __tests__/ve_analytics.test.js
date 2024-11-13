/**
 * File: ve_analytics.test.js
 * 
 * Description: This file contains tests for the VE Analytics page functionality.
 * 
 * @jest-environment jsdom
 */

require('../openwaves/static/js/analytics');

describe('VE Analytics Functionality', () => {
    let poolSelect, questionRows;

    beforeEach(() => {
        // Set up the DOM with elements required for the tests
        document.body.innerHTML = `
            <form id="questionForm">
                <select id="pool">
                    <option value="1">Pool 1</option>
                    <option value="2">Pool 2</option>
                </select>
            </form>
            <table>
                <tr class="question-row" data-question-id="1"></tr>
                <tr class="question-row" data-question-id="2"></tr>
                <tr id="details-1" class="is-hidden"></tr>
                <tr id="details-2" class="is-hidden"></tr>
            </table>
        `;

        poolSelect = document.getElementById('pool');
        questionRows = document.querySelectorAll('.question-row');

        // Mock the form's submit function
        poolSelect.form.submit = jest.fn();

        // Simulate DOMContentLoaded to initialize event listeners in questionDetail.js
        document.dispatchEvent(new Event('DOMContentLoaded'));
    });

    /**
     * Test ID: UT-267
     * 
     * This test verifies that changing the `pool` selection auto-submits the form.
     * 
     * Asserts:
     * - The form's submit method is called on pool selection change.
     */
    test('auto-submits form on pool selection change', () => {
        // Simulate changing the pool selection
        const changeEvent = new Event('change');
        poolSelect.dispatchEvent(changeEvent);

        // Verify that form.submit() was called
        expect(poolSelect.form.submit).toHaveBeenCalled();
    });

    /**
     * Test ID: UT-268
     * 
     * This test ensures that clicking a question row toggles the visibility of the associated details row.
     * 
     * Asserts:
     * - The "is-hidden" class is removed on the first click, making the row visible.
     * - The "is-hidden" class is added again on the second click, hiding the row.
     */
    test('toggles question detail visibility on row click', () => {
        const row = questionRows[0];
        const questionId = row.getAttribute('data-question-id');
        const detailRow = document.getElementById(`details-${questionId}`);

        // Simulate clicking the question row to show details
        row.click();
        expect(detailRow.classList.contains('is-hidden')).toBe(false);

        // Simulate another click to hide details
        row.click();
        expect(detailRow.classList.contains('is-hidden')).toBe(true);
    });

    /**
     * Test ID: UT-269
     * 
     * Test that the code handles missing pool element gracefully.
     * 
     * Asserts:
     * - No errors occur when the pool select element is missing.
     */
    test('does not throw error when pool select element is missing', () => {
        document.getElementById('pool').remove();

        expect(() => {
            document.dispatchEvent(new Event('DOMContentLoaded'));
        }).not.toThrow();
    });

    /**
     * Test ID: UT-270
     * 
     * Test that the code handles missing form on pool select element gracefully.
     * 
     * Asserts:
     * - No errors occur if the pool select element lacks a form.
     */
    test('does not throw error on pool change if form is missing', () => {
        delete poolSelect.form; // Remove the form reference

        expect(() => {
            poolSelect.dispatchEvent(new Event('change'));
        }).not.toThrow();
    });

    /**
     * Test ID: UT-271
     * 
     * Test that clicking a row without an associated detail row does not throw an error.
     * 
     * Asserts:
     * - No errors occur if there is no associated detail row for the clicked question row.
     */
    test('does not throw error when details row is missing', () => {
        const row = questionRows[0];
        row.setAttribute('data-question-id', '3'); // Set to a non-existent detail row

        expect(() => row.click()).not.toThrow();
    });

    /**
     * Test ID: UT-272
     * 
     * This test verifies that clicking a question row without a question ID does not throw an error.
     * 
     * Asserts:
     * - No errors occur if a question row lacks a data-question-id attribute.
     */
    test('does not throw error when question row lacks data-question-id', () => {
        const row = questionRows[0];
        row.removeAttribute('data-question-id');

        expect(() => row.click()).not.toThrow();
    });
});
