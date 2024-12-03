/**
 * File: pools.test.js
 * 
 * Description: This file contains unit tests for the pools page functionality.
 * 
 * @jest-environment jsdom
 */


describe('Pool management functionality', () => {
    let csrfTokenInput;
    let poolRow, expandableRow;

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
        <div class="container has-text-centered">
            <!-- Flash messages -->
            <div class="column is-8 is-offset-2">
                <div class="box">
                    <h3 class="title has-text-centered has-text-dark">Question Pools</h3>
                    <div class="table-container has-text-centered">
                        <table class="table is-striped is-hoverable is-fullwidth">
                        <thead>
                            <tr>
                                <th>Pool ID</th>
                                <th>Pool Name</th>
                                <th>Element</th>
                                <th>Start Date</th>
                                <th>End Date</th>
                                <th>Questions</th>
                            </tr>
                        </thead>
                        
                        <tbody>
                            
                            <tr class="pool-row" data-id="1">
                                <td>1</td>
                                <td>Technician</td>
                                <td>2</td>
                                <td>2024-07-01</td>
                                <td>2028-06-30</td>
                                <td>
                                    
                                        411 questions
                                    
                                </td>
                                <td>
                                    <button class="button is-small is-danger delete-pool-button" data-name="Technician" data-id="1">Delete</button>
                                </td>
                            </tr>
                            <tr class="expandable-row" data-id="1">
                                <td colspan="7">
                                    <div id="fullscreen-overlay" class="fullscreen-overlay">
                                            <img id="fullscreen-image" class="fullscreen-image" src="" alt="Blown-up Diagram">
                                        </div><table class="table is-striped is-fullwidth">
                                        <thead>
                                            <tr>
                                                <th>Diagram ID</th>
                                                <th>Diagram Name</th>
                                                <th>Image</th>
                                            </tr>
                                        </thead>
                                        
                                        <tbody>
                                            
                                            
                                            <tr>
                                                <td>1</td>
                                                <td>T-1</td>
                                                <td><img src="/static/images/diagrams/1_T1.jpg" alt="T-1" class="pool-diagram thumbnail-image"></td>
                                                <td>
                                                    <button class="button is-small is-danger delete-diagram-button" data-name="diagrams/1_T1.jpg" data-id="1">Delete</button>
                                                </td>
                                            </tr>
                                            
                                            <tr>
                                                <td colspan="4">
                                                    <button class="button is-small is-light-button-color upload-diagram-button" data-name="Technician" data-id="1">Upload</button>
                                                </td>
                                            </tr>
                                            
                                    </tbody></table>
                                    <!-- Modal for CSV and Image upload for this pool -->
                                    <div class="modal" id="upload-modal-1">
                                        <div class="modal-background"></div>
                                        <div class="modal-card">
                                            <header class="modal-card-head">
                                                <p class="modal-card-title">Upload Diagram for Technician</p>
                                                <button class="delete close-modal" aria-label="close"></button>
                                            </header>
                                            <section class="modal-card-body">
                                                <form id="upload-form-1" enctype="multipart/form-data">
                                                    
                                                        <input type="hidden" name="csrf_token" value="dummy-csrf-token">
                                                    

                                                    <!-- Diagram Name Field (Readonly) -->
                                                    <div class="field">
                                                        <label class="label">Diagram Name</label>
                                                        <div class="control">
                                                            <input class="input" type="text" name="diagram_name" value="">
                                                        </div>
                                                        <p class="help">Please enter the diagram name based on the element and current number (e.g., T-1, G-1, E-1).</p>
                                                    </div>

                                                    <!-- Upload Image File Field -->
                                                    <div class="field">
                                                        <label class="label">Upload Image File</label>
                                                        <div class="control">
                                                            <input class="input" type="file" name="file" accept="image/*" required="">
                                                        </div>
                                                    </div>
                                                </form>
                                            </section>
                                            <footer class="modal-card-foot">
                                                <button class="button is-success submit-upload" data-pool-id="1">Upload</button>
                                                <button class="button close-modal">Cancel</button>
                                            </footer>
                                        </div>
                                    </div>
                                    
                            </td></tr><tr class="pool-row" data-id="2">
                                <td>2</td>
                                <td>General</td>
                                <td>3</td>
                                <td>2024-07-01</td>
                                <td>2028-06-30</td>
                                <td>
                                    
                                        427 questions
                                    
                                </td>
                                <td>
                                    <button class="button is-small is-danger delete-pool-button" data-name="General" data-id="2">Delete</button>
                                </td>
                            </tr>
                            <tr class="expandable-row" data-id="2">
                                <td colspan="7">
                                    <div id="fullscreen-overlay" class="fullscreen-overlay">
                                            <img id="fullscreen-image" class="fullscreen-image" src="" alt="Blown-up Diagram">
                                        </div><table class="table is-striped is-fullwidth">
                                        <thead>
                                            <tr>
                                                <th>Diagram ID</th>
                                                <th>Diagram Name</th>
                                                <th>Image</th>
                                            </tr>
                                        </thead>
                                        
                                        <tbody>
                                            
                                            <tr>
                                                <td colspan="4">No diagrams found.</td>
                                                <td>
                                                    <button class="button is-small is-light-button-color upload-diagram-button" data-name="General" data-id="2">Upload</button>
                                                </td>
                                            </tr>
                                            
                                    </tbody></table>
                                    <!-- Modal for CSV and Image upload for this pool -->
                                    <div class="modal" id="upload-modal-2">
                                        <div class="modal-background"></div>
                                        <div class="modal-card">
                                            <header class="modal-card-head">
                                                <p class="modal-card-title">Upload Diagram for General</p>
                                                <button class="delete close-modal" aria-label="close"></button>
                                            </header>
                                            <section class="modal-card-body">
                                                <form id="upload-form-2" enctype="multipart/form-data">
                                                    
                                                        <input type="hidden" name="csrf_token" value="dummy-csrf-token">
                                                    

                                                    <!-- Diagram Name Field (Readonly) -->
                                                    <div class="field">
                                                        <label class="label">Diagram Name</label>
                                                        <div class="control">
                                                            <input class="input" type="text" name="diagram_name" value="">
                                                        </div>
                                                        <p class="help">Please enter the diagram name based on the element and current number (e.g., T-1, G-1, E-1).</p>
                                                    </div>

                                                    <!-- Upload Image File Field -->
                                                    <div class="field">
                                                        <label class="label">Upload Image File</label>
                                                        <div class="control">
                                                            <input class="input" type="file" name="file" accept="image/*" required="">
                                                        </div>
                                                    </div>
                                                </form>
                                            </section>
                                            <footer class="modal-card-foot">
                                                <button class="button is-success submit-upload" data-pool-id="2">Upload</button>
                                                <button class="button close-modal">Cancel</button>
                                            </footer>
                                        </div>
                                    </div>
                                    
                            </td></tr><tr class="pool-row" data-id="3">
                                <td>3</td>
                                <td>Extra</td>
                                <td>4</td>
                                <td>2024-07-01</td>
                                <td>2028-06-30</td>
                                <td>
                                    
                                        <!-- Display upload button when there are no questions -->
                                        <button class="button is-small is-light-button-color" id="upload-button-3">Upload Questions</button>
                        
                                        <!-- Modal for CSV upload -->
                                        <div class="modal" id="upload-modal-3">
                                            <div class="modal-background"></div>
                                            <div class="modal-card">
                                                <header class="modal-card-head">
                                                    <p class="modal-card-title">Upload Questions for Extra</p>
                                                    <button class="delete" aria-label="close"></button>
                                                </header>
                                                <section class="modal-card-body">
                                                    <form id="upload-form-3" enctype="multipart/form-data">
                                                        
                                                            <input type="hidden" name="csrf_token" value="dummy-csrf-token">
                                                        
                                                        
                                                        <div class="field">
                                                            <label class="label">Upload CSV File</label>
                                                            <div class="control">
                                                                <input class="input" type="file" name="file" accept=".csv" required="">
                                                            </div>
                                                        </div>
                                                    </form>
                                                </section>
                                                <footer class="modal-card-foot">
                                                    <button class="button is-light-button-color" id="submit-upload-3">Upload</button>
                                                    <button class="button is-button-color">Cancel</button>
                                                </footer>
                                            </div>
                                        </div>
                                    
                                </td>
                                <td>
                                    <button class="button is-small is-danger delete-pool-button" data-name="Extra" data-id="3">Delete</button>
                                </td>
                            </tr>
                            <tr class="expandable-row" data-id="3">
                                <td colspan="7">
                                    <div id="fullscreen-overlay" class="fullscreen-overlay">
                                            <img id="fullscreen-image" class="fullscreen-image" src="" alt="Blown-up Diagram">
                                        </div><table class="table is-striped is-fullwidth">
                                        <thead>
                                            <tr>
                                                <th>Diagram ID</th>
                                                <th>Diagram Name</th>
                                                <th>Image</th>
                                            </tr>
                                        </thead>
                                        
                                        <tbody>
                                            
                                            <tr>
                                                <td colspan="4">No diagrams found.</td>
                                                <td>
                                                    <button class="button is-small is-light-button-color upload-diagram-button" data-name="Extra" data-id="3">Upload</button>
                                                </td>
                                            </tr>
                                            
                                    </tbody></table>
                                    <!-- Modal for CSV and Image upload for this pool -->
                                    <div class="modal" id="upload-modal-3">
                                        <div class="modal-background"></div>
                                        <div class="modal-card">
                                            <header class="modal-card-head">
                                                <p class="modal-card-title">Upload Diagram for Extra</p>
                                                <button class="delete close-modal" aria-label="close"></button>
                                            </header>
                                            <section class="modal-card-body">
                                                <form id="upload-form-3" enctype="multipart/form-data">
                                                    
                                                        <input type="hidden" name="csrf_token" value="dummy-csrf-token">
                                                    

                                                    <!-- Diagram Name Field (Readonly) -->
                                                    <div class="field">
                                                        <label class="label">Diagram Name</label>
                                                        <div class="control">
                                                            <input class="input" type="text" name="diagram_name" value="">
                                                        </div>
                                                        <p class="help">Please enter the diagram name based on the element and current number (e.g., T-1, G-1, E-1).</p>
                                                    </div>

                                                    <!-- Upload Image File Field -->
                                                    <div class="field">
                                                        <label class="label">Upload Image File</label>
                                                        <div class="control">
                                                            <input class="input" type="file" name="file" accept="image/*" required="">
                                                        </div>
                                                    </div>
                                                </form>
                                            </section>
                                            <footer class="modal-card-foot">
                                                <button class="button is-success submit-upload" data-pool-id="3">Upload</button>
                                                <button class="button close-modal">Cancel</button>
                                            </footer>
                                        </div>
                                    </div>
                                    
                                </td>
                            </tr>                
                        </tbody>
                        
                        </table>
                    </div>

                    <!-- Button to create a new pool -->
                    <div class="has-text-centered">
                        <button class="button is-button-color" id="create-pool-button">Create New Pool</button>
                    </div>

                    <!-- Modal for creating a new question pool -->
                    <div class="modal" id="create-pool-modal">
                        <div class="modal-background"></div>
                        <div class="modal-card">
                            <header class="modal-card-head">
                                <p class="modal-card-title">Create Question Pool</p>
                                <button class="delete close-modal" aria-label="close"></button>
                            </header>
                            <section class="modal-card-body">
                                <form id="create-pool-form">
                                    
                                        <input type="hidden" name="csrf_token" value="dummy-csrf-token">
                                    

                                    <!-- Dropdown for Pool Name -->
                                    <div class="field">
                                        <label class="label">Element Pool</label>
                                        <div class="control">
                                            <div class="select">
                                                <select id="pool-name" name="pool_name" required="">
                                                    <option value="Technician">Technician</option>
                                                    <option value="General">General</option>
                                                    <option value="Extra">Extra</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Hidden Element field that gets auto-filled -->
                                    <input type="hidden" id="exam-element" name="exam_element" value="2">

                                    <!-- Auto-populated Start Date -->
                                    <div class="field">
                                        <label class="label">Start Date</label>
                                        <div class="control">
                                            <input class="input" type="date" id="start-date" name="start_date" required="">
                                        </div>
                                    </div>

                                    <!-- Auto-populated End Date -->
                                    <div class="field">
                                        <label class="label">End Date</label>
                                        <div class="control">
                                            <input class="input" type="date" id="end-date" name="end_date" required="">
                                        </div>
                                    </div>
                                </form>
                            </section>
                            <footer class="modal-card-foot">
                                <button class="button is-success" id="submit-pool-form">Save</button>
                                <button class="button is-light" id="cancel-pool-form">Cancel</button>
                            </footer>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        `;

        // Mock console.error to track errors
        console.error = jest.fn();

        csrfTokenInput = document.querySelector('input[name="csrf_token"]');
        
        // Mock window.confirm and window.alert to prevent actual prompts during tests
        jest.spyOn(window, 'confirm').mockImplementation(() => true);
        jest.spyOn(window, 'alert').mockImplementation(() => {});
        jest.spyOn(console, 'error').mockImplementation(() => {});
    
        // Mock fetch API
        global.fetch = jest.fn(() => Promise.resolve({ ok: true }));

        // Require pools.js in an isolated module context
        jest.isolateModules(() => {
            require('../openwaves/static/js/pools');
        });

        // Simulate DOMContentLoaded to initialize event listeners
        document.dispatchEvent(new Event('DOMContentLoaded'));

        // Now assign poolRow and expandableRow after event listeners are attached
        poolRow = document.querySelector('.pool-row');
        expandableRow = document.querySelector('.expandable-row');

        consoleErrorMock = jest.spyOn(console, 'error').mockImplementation(() => {});
    });
        
    afterEach(() => {
        jest.resetModules();
        jest.clearAllMocks();
        document.body.innerHTML = '';
    });

    /**
     * Test ID: UT-82
     * Test the functionality of the upload button triggering modal visibility.
     *
     * This test ensures that clicking the upload button opens the corresponding modal, 
     * allowing users to interact with the upload form.
     *
     * Asserts:
     * - The modal becomes active (is shown) after clicking the upload button.
     */
    test('upload button triggers modal visibility', () => {
        const uploadButton = document.getElementById('upload-button-3');
        const modal = document.getElementById('upload-modal-3');
        
        // Simulate clicking the upload button
        uploadButton.click();
        
        // Assert the modal becomes active
        expect(modal.classList.contains('is-active')).toBe(true);
    });

    /**
     * Test ID: UT-83
     * Test the functionality of closing the modal when the cancel button is clicked.
     *
     * This test ensures that clicking the cancel button properly closes the create pool modal,
     * preventing any unintended interactions while the modal is open.
     *
     * Asserts:
     * - The modal starts as active (open).
     * - The modal is closed after the cancel button is clicked.
     */
    test('close create-pool-modal when cancel is clicked', () => {
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
     * Test ID: UT-84
     * Test the functionality of closing the modal when the close button (X) is clicked.
     *
     * This test ensures that clicking the close button properly closes the create pool modal,
     * preventing any unintended interactions while the modal is open.
     *
     * Asserts:
     * - The modal starts as active (open).
     * - The modal is closed after the close button is clicked.
     */
    test('close create-pool-modal when X is clicked', async () => {    
        const closeButton = document.querySelector('#create-pool-modal .delete');
        const modal = document.getElementById('create-pool-modal');
    
        // Open the modal
        modal.classList.add('is-active');
    
        // Ensure the modal starts as active (open)
        expect(modal.classList.contains('is-active')).toBe(true);
    
        // Simulate the click event
        closeButton.click();
    
        // Wait for any asynchronous actions to complete (this ensures that event listeners are executed)
        await new Promise((resolve) => setTimeout(resolve, 0));
    
        // Assert that the modal is no longer active
        expect(modal.classList.contains('is-active')).toBe(false);
    });

    /**
     * Test ID: UT-85
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
     * Test ID: UT-86
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
     * Test ID: UT-87
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
     * Test ID: UT-88
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
     * Test ID: UT-89
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
     * Test ID: UT-90
     * Test the functionality of clicking a pool row to add the "show" class if the expandable row is hidden.
     *
     * This test ensures that when a pool row is clicked and the expandable row is initially hidden,
     * the "show" class is added to make it visible.
     *
     * Asserts:
     * - Clicking a pool row adds the "show" class to the expandable row when it is hidden.
     */
    test('clicking a pool row adds "show" class if expandable row is hidden', async () => {
        // Initially, the expandable row should not have the "show" class
        expect(expandableRow.classList.contains('show')).toBe(false);
    
        // Simulate clicking the pool row
        poolRow.click();
    
        // Wait for any asynchronous code to complete
        await Promise.resolve();
    
        // Now, check if the "show" class has been added
        expect(expandableRow.classList.contains('show')).toBe(true);
    });
    
    /**
     * Test ID: UT-91
     * Test the functionality of clicking a pool row to remove the "show" class if the expandable row is shown.
     *
     * This test ensures that when a pool row is clicked and the expandable row is initially shown,
     * the "show" class is removed to hide it.
     *
     * Asserts:
     * - Clicking a pool row removes the "show" class from the expandable row when it is visible.
     */
    test('clicking a pool row removes "show" class if expandable row is shown', () => {
        // Add the "show" class initially
        expandableRow.classList.add('show');
        expect(expandableRow.classList.contains('show')).toBe(true);

        // Click the pool row
        poolRow.click();

        // The "show" class should now be removed
        expect(expandableRow.classList.contains('show')).toBe(false);
    });

    /**
     * Test ID: UT-92
     * Test the functionality of clicking a pool row when no corresponding expandable row is found.
     *
     * This test ensures that when a pool row is clicked, but no expandable row with the matching data-id exists,
     * an error is logged to the console.
     *
     * Asserts:
     * - If no expandable row exists, an error is logged with the correct message.
     */
    test('clicking a pool row logs an error if no expandable row is found', () => {
        // Remove the expandable row from the DOM
        expandableRow.remove();

        // Click the pool row
        poolRow.click();

        // Ensure console.error is called with the correct message
        expect(console.error).toHaveBeenCalledWith('No expandable row found for pool ID: 1');
    });

    /**
     * Test ID: UT-93
     * Test the functionality of clicking the upload button to show the modal.
     *
     * This test ensures that clicking the "Upload" button opens the corresponding modal.
     *
     * Asserts:
     * - Clicking the "Upload" button adds the "is-active" class to the modal.
     */
    test('clicking the upload button shows the corresponding modal', () => {
        // Simulate clicking the upload button
        const uploadButton = document.getElementById('upload-button-3');
        const modal = document.getElementById('upload-modal-3');
    
        // Initially, the modal should not be active
        expect(modal.classList.contains('is-active')).toBe(false);
    
        uploadButton.click();
    
        // Assert that the modal becomes active (is shown)
        expect(modal.classList.contains('is-active')).toBe(true);
    });

    /**
     * Test ID: UT-94
     * Test the functionality of clicking on a thumbnail image to show the fullscreen overlay.
     *
     * This test ensures that clicking the thumbnail image sets the fullscreen image src
     * and makes the fullscreen overlay visible.
     *
     * Asserts:
     * - The fullscreen overlay becomes visible when clicking the thumbnail image.
     * - The fullscreen image's source is correctly set to the thumbnail image's source.
     */
    test('clicking thumbnail image shows fullscreen overlay', () => {
        // Reference the thumbnail image and fullscreen elements
        const thumbnailImage = document.querySelector('.thumbnail-image');
        const fullscreenOverlay = document.getElementById('fullscreen-overlay');
        const fullscreenImage = document.getElementById('fullscreen-image');

        // Simulate clicking the thumbnail image
        thumbnailImage.click();

        // Assert that the fullscreen image source is set correctly
        expect(fullscreenImage.src).toContain('http://localhost/static/images/diagrams/1_T1.jpg');

        // Assert that the fullscreen overlay becomes visible
        expect(fullscreenOverlay.style.display).toBe('flex');
    });

    /**
     * Test ID: UT-95
     * Test the functionality of clicking the fullscreen overlay to hide it.
     *
     * This test ensures that clicking the fullscreen overlay hides it from view.
     *
     * Asserts:
     * - The fullscreen overlay becomes hidden after clicking it.
     */
    test('clicking fullscreen overlay hides it', () => {
        // Reference the fullscreen overlay element
        const fullscreenOverlay = document.getElementById('fullscreen-overlay');

        // Simulate opening the fullscreen overlay by setting its display to 'flex'
        fullscreenOverlay.style.display = 'flex';

        // Ensure the overlay is initially visible
        expect(fullscreenOverlay.style.display).toBe('flex');

        // Simulate clicking the fullscreen overlay to close it
        fullscreenOverlay.click();

        // Assert that the overlay is hidden after clicking
        expect(fullscreenOverlay.style.display).toBe('none');
    });
    
    /**
     * Test ID: UT-96
     * Test the functionality of clicking the "Upload" button to open the upload modal.
     *
     * This test ensures that clicking the "Upload" button opens the corresponding modal.
     *
     * Asserts:
     * - Clicking the "Upload" button adds the "is-active" class to the modal.
     */
    test('UT-156: Open upload modal when "Upload" button is clicked', () => {
        // Reference the upload button and the modal elements
        const uploadButton = document.querySelector('.upload-diagram-button');
        const modal = document.getElementById('upload-modal-1');

        // Simulate clicking the upload button
        uploadButton.click();

        // Assert that the modal becomes active (is shown)
        expect(modal.classList.contains('is-active')).toBe(true);
    });
});
