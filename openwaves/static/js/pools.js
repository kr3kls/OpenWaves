document.addEventListener('DOMContentLoaded', function() {
    // Handle deleting pools
    document.querySelectorAll('.delete-pool-button').forEach(button => {
        button.addEventListener('click', function() {
            const poolId = this.getAttribute('data-id');
            const poolName = this.getAttribute('data-name');
            const csrfToken = document.querySelector('input[name="csrf_token"]').value;

            if (confirm("Are you sure you want to delete the " + poolName + " pool and all associated questions?")) {
                fetch(`/delete_pool/${poolId}`, {
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
    document.querySelectorAll('.delete').forEach(button => {
        button.addEventListener('click', function() {
            const modalId = this.closest('.modal').id;
            document.getElementById(modalId).classList.remove('is-active');
        });
    });

    document.querySelectorAll('[id^=submit-upload]').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const poolId = this.id.split('-')[2];
            const form = document.getElementById('upload-form-' + poolId);
            const formData = new FormData(form);

            // Submit the form data via AJAX to the server
            const response = await fetch(`/upload_questions/${poolId}`, {
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
    createPoolButton.addEventListener('click', function() {
        // Set default start and end dates
        const currentYear = new Date().getFullYear();
        startDateField.value = `${currentYear}-07-01`;
        endDateField.value = `${currentYear + 4}-06-30`;

        // Open the modal
        createPoolModal.classList.add('is-active');
    });

    // Close modal on clicking the 'Cancel' button or 'X'
    document.querySelector('.delete').addEventListener('click', function() {
        createPoolModal.classList.remove('is-active');
    });

    document.getElementById('cancel-pool-form').addEventListener('click', function() {
        createPoolModal.classList.remove('is-active');
    });

    // Handle pool name change to update the exam element automatically
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

    // Automatically update end date based on start date
    startDateField.addEventListener('change', function() {
        const startDate = new Date(startDateField.value);
        if (startDate) {
            const endDate = new Date(startDate);
            endDate.setFullYear(startDate.getFullYear() + 4);  // Add 4 years
            endDateField.value = `${endDate.getFullYear()}-06-30`;  // Always set end date to June 30
        }
    });

    // Handle form submission
    document.getElementById('submit-pool-form').addEventListener('click', async function(e) {
        e.preventDefault();

        const formData = new FormData(document.getElementById('create-pool-form'));

        // Submit the form data via AJAX to the server
        const response = await fetch('/create_pool', {
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
});
