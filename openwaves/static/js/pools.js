document.addEventListener('DOMContentLoaded', function() {
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
    
    // Toggle the create pool modal
    document.getElementById('create-pool-button').addEventListener('click', function() {
        document.getElementById('create-pool-modal').classList.add('is-active');
    });

    // Close modal on clicking the 'Cancel' button or 'X'
    document.querySelector('.delete').addEventListener('click', function() {
        document.getElementById('create-pool-modal').classList.remove('is-active');
    });

    document.getElementById('cancel-pool-form').addEventListener('click', function() {
        document.getElementById('create-pool-modal').classList.remove('is-active');
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
        document.getElementById('create-pool-modal').classList.remove('is-active');
    });
});