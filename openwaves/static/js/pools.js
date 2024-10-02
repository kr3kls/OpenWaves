document.addEventListener('DOMContentLoaded', function() {
    // Handle deleting pools
    document.querySelectorAll('.delete-pool-button').forEach(button => {
        button.addEventListener('click', function() {
            const poolId = this.getAttribute('data-id');
            const poolName = this.getAttribute('data-name');
            const csrfToken = document.querySelector('input[name="csrf_token"]').value;

            if (confirm("Are you sure you want to delete the " + poolName + " pool and all associated questions?")) {
                fetch(`/ve/delete_pool/${poolId}`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => {
                    if (response.ok) {
                        alert('Pool deleted successfully.');
                        location.reload();  // Reload the page to reflect changes
                    } else {
                        alert('There was an error deleting the pool.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('There was an error deleting the pool.');
                });
            }
        });
    });

    // Toggle the upload modal
    document.querySelectorAll('[id^=upload-button]').forEach(button => {
        button.addEventListener('click', function() {
            const poolId = this.id.split('-')[2];
            document.getElementById('upload-modal-' + poolId).classList.add('is-active');
        });
    });

    // Close modal on clicking the 'Cancel' button or 'X'
    const deleteButton = document.querySelector('.delete');
    if (deleteButton) {
        document.querySelectorAll('.delete').forEach(button => {
            button.addEventListener('click', function() {
                const modalId = this.closest('.modal').id;
                document.getElementById(modalId).classList.remove('is-active');
            });
        });
    }
    

    document.querySelectorAll('[id^=submit-upload]').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const poolId = this.id.split('-')[2];
            const form = document.getElementById('upload-form-' + poolId);
            const formData = new FormData(form);

            // Submit the form data via AJAX to the server
            const response = await fetch(`/ve/upload_questions/${poolId}`, {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                alert('Questions uploaded successfully!');
                location.reload();  // Reload the page to show the new questions
            } else {
                alert('There was an error uploading the questions.');
            }

            // Close the modal after form submission
            document.getElementById('upload-modal-' + poolId).classList.remove('is-active');
        });
    });

    // Handle creating a new pool
    const createPoolButton = document.getElementById('create-pool-button');
    const createPoolModal = document.getElementById('create-pool-modal');
    const poolNameDropdown = document.getElementById('pool-name');
    const examElementField = document.getElementById('exam-element');
    const startDateField = document.getElementById('start-date');
    const endDateField = document.getElementById('end-date');

    // Toggle the create pool modal
    if (createPoolButton) {
        createPoolButton.addEventListener('click', function() {
            // Set default start and end dates
            const currentYear = new Date().getFullYear();
            startDateField.value = `${currentYear}-07-01`;
            endDateField.value = `${currentYear + 4}-06-30`;
    
            // Open the modal
            createPoolModal.classList.add('is-active');
        });
    }
    
    // Close modal on clicking the 'Cancel' button or 'X'
    if (deleteButton) {
        document.querySelector('.delete').addEventListener('click', function() {
            createPoolModal.classList.remove('is-active');
        });
    }
    

    // Close modal on clicking the 'Cancel' button
    const cancelPoolForm = document.getElementById('cancel-pool-form');
    if (cancelPoolForm) {
        document.getElementById('cancel-pool-form').addEventListener('click', function() {
            createPoolModal.classList.remove('is-active');
        });
    }
    

    // Handle pool name change to update the exam element automatically
    if (poolNameDropdown) {
        poolNameDropdown.addEventListener('change', function() {
            const selectedPool = poolNameDropdown.value;
            if (selectedPool === 'Technician') {
                examElementField.value = 2;
            } else if (selectedPool === 'General') {
                examElementField.value = 3;
            } else if (selectedPool === 'Extra') {
                examElementField.value = 4;
            }
        });
    }

    // Automatically update end date based on start date
    if (startDateField) {
        startDateField.addEventListener('change', function() {
            const startDate = new Date(startDateField.value);
            if (startDate) {
                const endDate = new Date(startDate);
                endDate.setFullYear(startDate.getFullYear() + 4);  // Add 4 years
                endDateField.value = `${endDate.getFullYear()}-06-30`;  // Always set end date to June 30
            }
        });
    }
    

    // Handle form submission
    const submitPoolForm = document.getElementById('submit-pool-form');
    if (submitPoolForm) {
        document.getElementById('submit-pool-form').addEventListener('click', async function(e) {
            e.preventDefault();

            const formData = new FormData(document.getElementById('create-pool-form'));

            // Submit the form data via AJAX to the server
            const response = await fetch('/ve/create_pool', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                alert('Pool created successfully!');
                location.reload();  // Reload the page to show the new pool
            } else {
                alert('There was an error creating the pool.');
            }

            // Close the modal after form submission
            createPoolModal.classList.remove('is-active');
        });
    }

    document.querySelectorAll('.pool-row').forEach(row => {
        row.addEventListener('click', function() {
            const poolId = this.getAttribute('data-id');

            const expandableRow = document.querySelector(`.expandable-row[data-id='${poolId}']`);
            if (expandableRow) {
                if (expandableRow.classList.contains('show')) {
                    expandableRow.classList.remove('show');
                } else {
                    expandableRow.classList.add('show');
                }
            } else {
                console.error(`No expandable row found for pool ID: ${poolId}`);
            }
        });
    });

    // Open the modal when the 'Upload' button is clicked
    document.querySelectorAll('.upload-diagram-button').forEach(button => {
        button.addEventListener('click', function() {
            const poolId = this.getAttribute('data-id');
            const modal = document.getElementById(`upload-modal-${poolId}`);
            console.log('Looking for modal:', modal);
            if (modal) {
                modal.classList.add('is-active');
            }
        });
    });

    // Close the modal when 'Cancel' button or 'X' button is clicked
    document.querySelectorAll('.close-modal').forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                modal.classList.remove('is-active');
            }
        });
    });

    // Handle the upload button in the modal
    document.querySelectorAll('.submit-upload').forEach(button => {
        button.addEventListener('click', async function() {
            const poolId = this.getAttribute('data-pool-id');
            const form = document.getElementById(`upload-form-${poolId}`);
            const formData = new FormData(form);

            try {
                const response = await fetch(`/ve/upload_diagram/${poolId}`, {
                    method: 'POST',
                    body: formData,
                });

                if (response.ok) {
                    alert('Diagram uploaded successfully!');
                    location.reload(); // Reload the page to show the new diagram
                } else {
                    alert('There was an error uploading the diagram.');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('There was an error uploading the diagram.');
            }

            // Close the modal after submission
            const modal = document.getElementById(`upload-modal-${poolId}`);
            if (modal) {
                modal.classList.remove('is-active');
            }
        });
    });
});
