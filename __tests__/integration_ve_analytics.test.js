/**
 * File: ve_analytics.test.js
 * 
 * Description: This file contains integration tests for the VE Analytics page functionality.
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

        // Simulate DOMContentLoaded to initialize event listeners
        document.dispatchEvent(new Event('DOMContentLoaded'));
    });

    /**
     * Test ID: IT-173
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
});
