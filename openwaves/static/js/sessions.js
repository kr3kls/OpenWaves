document.addEventListener('DOMContentLoaded', () => {
    // Function to set date in modal
    const startDateField = document.getElementById('start-date');
    if (startDateField) {
        const today = new Date();
        const formattedDate = today.toISOString().split('T')[0];  // Format as YYYY-MM-DD
        startDateField.value = formattedDate;  // Set today's date as the default value
    }

    // Function to handle modal opening
    function openModal(modal) {
        modal.classList.add('is-active');
    }

    // Function to handle modal closing
    function closeModal(modal) {
        modal.classList.remove('is-active');
    }

    // Close modals on clicking "Cancel" or background
    document.querySelectorAll('.modal').forEach((modal) => {
        modal.querySelector('.delete').addEventListener('click', () => closeModal(modal));
        modal.querySelector('.button.is-light-button-color').addEventListener('click', () => closeModal(modal));
        modal.querySelector('.modal-background').addEventListener('click', () => closeModal(modal));
    });

    // Open the modal for creating a new session
    const createSessionButton = document.getElementById('create-session-button');
    const createSessionModal = document.getElementById('create-session-modal');
    createSessionButton.addEventListener('click', () => openModal(createSessionModal));

    // Handle session creation form submission
    const submitSessionForm = document.getElementById('submit-session-form');
    const createSessionForm = document.getElementById('create-session-form');
    submitSessionForm.addEventListener('click', (e) => {
        e.preventDefault();
        const formData = new FormData(createSessionForm);
        fetch('/create_session', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error creating session: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while creating the session.');
        });
    });

    // Handle delete button click for each session
    document.querySelectorAll('.delete-session-button').forEach((button) => {
        button.addEventListener('click', () => {
            const sessionId = button.getAttribute('data-id');
            if (confirm('Are you sure you want to delete this session?')) {
                fetch(`/delete_session/${sessionId}`, {
                    method: 'DELETE',
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Reload the page to show the updated session list (or update dynamically if preferred)
                        location.reload();
                    } else {
                        alert('Error deleting session: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while deleting the session.');
                });
            }
        });
    });

    // Function to handle opening a session
    document.querySelectorAll('.open-session-button').forEach((button) => {
        button.addEventListener('click', () => {
            const sessionId = button.getAttribute('data-id');
            fetch(`/open_session/${sessionId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
                },
                body: JSON.stringify({ action: 'open' })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();  // Reload the page to reflect changes
                } else {
                    alert('Error opening session: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while opening the session.');
            });
        });
    });

    // Function to handle closing a session
    document.querySelectorAll('.close-session-button').forEach((button) => {
        button.addEventListener('click', () => {
            const sessionId = button.getAttribute('data-id');
            fetch(`/close_session/${sessionId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
                },
                body: JSON.stringify({ action: 'close' })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();  // Reload the page to reflect changes
                } else {
                    alert('Error closing session: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while closing the session.');
            });
        });
    });

});
