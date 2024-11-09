if (!window.poolsEventListenersInitialized) {
    window.poolsEventListenersInitialized = true;
    document.addEventListener('DOMContentLoaded', function() {

        // Utility function to close modals
        function closeModal(modal) {
            if (modal) {
                modal.classList.remove('is-active');
            }
        }

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

        // Handle deleting diagrams
        document.querySelectorAll('.delete-diagram-button').forEach(button => {
            button.addEventListener('click', function() {
                const diagramId = this.getAttribute('data-id');
                const diagramPath = this.getAttribute('data-name');
                const csrfToken = document.querySelector('input[name="csrf_token"]').value;

                if (confirm("Are you sure you want to delete the " + diagramPath + " diagram?")) {
                    fetch(`/ve/delete_diagram/${diagramId}`, {
                        method: 'DELETE',
                        headers: {
                            'X-CSRFToken': csrfToken,
                            'Content-Type': 'application/json'
                        }
                    })
                    .then(response => {
                        if (response.ok) {
                            alert('Diagram deleted successfully.');
                            location.reload();  // Reload the page to reflect changes
                        } else {
                            alert('There was an error deleting the diagram.');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('There was an error deleting the diagram.');
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

        // Close modals on clicking the 'Cancel' button, 'X', or any element with class 'close-modal'
        document.querySelectorAll('.close-modal').forEach(button => {
            button.addEventListener('click', function() {
                const modal = this.closest('.modal');
                closeModal(modal);
            });
        });

        // Handle form submission for uploading questions
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
                closeModal(document.getElementById('upload-modal-' + poolId));
            });
        });

        // Handle creating a new pool
        const createPoolButton = document.getElementById('create-pool-button');
        const createPoolModal = document.getElementById('create-pool-modal');
        const poolNameDropdown = document.getElementById('pool-name');
        const examElementField = document.getElementById('exam-element');
        const startDateField = document.getElementById('start-date');
        const endDateField = document.getElementById('end-date');

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

        // Handle canceling create pool form
        document.getElementById('cancel-pool-form')?.addEventListener('click', () => {
            closeModal(createPoolModal);
        });

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
                    endDate.setFullYear(startDate.getFullYear() + 4);
                    endDateField.value = `${endDate.getFullYear()}-06-30`;
                }
            });
        }

        // Handle form submission for creating a new pool
        document.getElementById('submit-pool-form')?.addEventListener('click', async function(e) {
            e.preventDefault();

            const formData = new FormData(document.getElementById('create-pool-form'));

            const response = await fetch('/ve/create_pool', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                alert('Pool created successfully!');
                location.reload();
            } else {
                alert('There was an error creating the pool.');
            }

            // Close the modal after form submission
            closeModal(createPoolModal);
        });

        // Toggle expandable pool rows
        document.querySelectorAll('.pool-row').forEach(row => {
            row.addEventListener('click', function(event) {
                // Check if any modal is active, and if so, prevent toggling
                const isAnyModalActive = document.querySelector('.modal.is-active');
                if (isAnyModalActive) {
                    return; // Don't toggle rows if a modal is open
                }

                // Proceed to toggle the expandable row if no modal is active
                const poolId = event.currentTarget.getAttribute('data-id');
                const expandableRow = document.querySelector(`.expandable-row[data-id='${poolId}']`);
                
                if (expandableRow) {
                    expandableRow.classList.toggle('show');
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
                if (modal) {
                    modal.classList.add('is-active');
                    modal.addEventListener('click', function(event) {
                        event.stopPropagation();
                    });
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

        // Handle image click to show enlarged version
        document.querySelectorAll('.thumbnail-image').forEach(image => {
            image.addEventListener('click', function() {
                const fullscreenOverlay = document.getElementById('fullscreen-overlay');
                const fullscreenImage = document.getElementById('fullscreen-image');

                fullscreenImage.src = this.src;
                fullscreenOverlay.style.display = 'flex';
            });
        });

        // Close fullscreen overlay when clicked
        document.getElementById('fullscreen-overlay')?.addEventListener('click', function() {
            this.style.display = 'none';
        });
    });
}
