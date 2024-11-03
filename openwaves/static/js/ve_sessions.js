// Helper function for making fetch requests with JSON response handling
function makeRequest(url, method, body = null, csrfToken = null) {
    const headers = { 'Content-Type': 'application/json' };
    if (csrfToken) headers['X-CSRFToken'] = csrfToken;

    return fetch(url, {
        method,
        headers,
        body: body ? JSON.stringify(body) : null,
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                const errorMessage = data.error || `Server responded with status: ${response.status}`;
                throw new Error(errorMessage);
            });
        }
        return response.json();
    });
}
// Conditionally export for testing if module.exports exists (Node.js)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { makeRequest };
}

document.addEventListener('DOMContentLoaded', () => {
    // Function to set date in modal
    const startDateField = document.getElementById('start-date');
    if (startDateField) {
        const today = new Date();
        const formattedDate = today.toISOString().split('T')[0];  // Format as YYYY-MM-DD
        startDateField.value = formattedDate;  // Set today's date as the default value
    }

    // Function to handle modal opening and closing
    function toggleModal(modal, action = 'open') {
        if (action === 'open') {
            modal.classList.add('is-active');
        } else {
            modal.classList.remove('is-active');
        }
    }

    // Add event listeners to modal close buttons
    function attachModalEvents() {
        document.querySelectorAll('.modal').forEach((modal) => {
            modal.querySelectorAll('.delete, .button.is-light-button-color, .modal-background')
                .forEach((closeElement) => {
                    closeElement.addEventListener('click', () => toggleModal(modal, 'close'));
                });
        });
    }

    // Handle session form submission
    function handleSessionFormSubmit() {
        const createSessionButton = document.getElementById('create-session-button');
        const createSessionModal = document.getElementById('create-session-modal');
        const submitSessionForm = document.getElementById('submit-session-form');
        const createSessionForm = document.getElementById('create-session-form');

        createSessionButton.addEventListener('click', () => toggleModal(createSessionModal, 'open'));

        submitSessionForm.addEventListener('click', (e) => {
            e.preventDefault();
            const formData = new FormData(createSessionForm);
            fetch('/ve/create_session', { method: 'POST', body: formData })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(data => {
                            throw new Error(data.error || `Server responded with status: ${response.status}`);
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    if (data && data.success) {
                        location.reload();
                    } else {
                        alert('Error creating session: ' + (data && data.error ? data.error : 'Unknown error'));
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert(error.message || 'An error occurred. Please try again.');
                });
        });        
    }

    // Generic function to handle session actions (open/close/delete)
    function handleSessionAction(buttonSelector, action, method = 'POST') {
        document.querySelectorAll(buttonSelector).forEach((button) => {
            button.addEventListener('click', () => {
                const sessionId = button.getAttribute('data-id');
                const csrfTokenInput = document.querySelector('input[name="csrf_token"]');
                const csrfToken = csrfTokenInput ? csrfTokenInput.value : null;
                const isForceClose = button.getAttribute('data-force') === 'true';

                const endpoint = getEndpoint(action, sessionId, isForceClose);

                if (action === 'delete' && !confirm('Are you sure you want to delete this session?')) return;
    
                // Set the request body only for non-DELETE requests
                const body = method === 'DELETE' ? null : JSON.stringify({ action });

                makeRequest(endpoint, method, { action }, csrfToken)
                    .then(data => {
                        if (data && data.success) {
                            location.reload();
                        } else {
                            alert(`Error ${action} session: ` + (data && data.error ? data.error : 'Unknown error'));
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert(error.message || 'An error occurred. Please try again.');

                        // If the error indicates an open session, update the button to "force close"
                        if (error.message === "There are still open exams in this session.") {
                            // Change the button to a "force close" action
                            button.setAttribute('data-force', 'true');
                            button.textContent = 'Force';
                            button.classList.remove('is-light-button-color');
                            button.classList.add('is-danger');
                        }
                    });
            });
        });
    }

    // Helper to determine the endpoint based on action and force state
    function getEndpoint(action, sessionId, isForceClose) {
        if (action === 'close' && isForceClose) {
            return `/ve/force_close_session/${sessionId}`;
        }
        return `/ve/${action}_session/${sessionId}`;
    }

    // Initialize all modal events
    attachModalEvents();

    // Initialize session form submit
    handleSessionFormSubmit();

    // Attach event listeners for session actions
    handleSessionAction('.delete-session-button', 'delete', 'DELETE');
    handleSessionAction('.open-session-button', 'open');
    handleSessionAction('.close-session-button', 'close');
});
