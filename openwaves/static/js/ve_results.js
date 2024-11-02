document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.clickable-row').forEach(row => {
        row.addEventListener('click', () => {
            const sessionId = row.getAttribute('data-session-id');
            const examElement = row.getAttribute('data-exam-element');
            const hcId = row.getAttribute('data-hc-id');

            // Create a form to submit data via POST
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/ve/exam/results';

            // Append hidden fields to the form
            const sessionInput = document.createElement('input');
            sessionInput.type = 'hidden';
            sessionInput.name = 'session_id';
            sessionInput.value = sessionId;
            form.appendChild(sessionInput);

            const elementInput = document.createElement('input');
            elementInput.type = 'hidden';
            elementInput.name = 'exam_element';
            elementInput.value = examElement;
            form.appendChild(elementInput);

            const hcInput = document.createElement('input');
            hcInput.type = 'hidden';
            hcInput.name = 'hc_id';
            hcInput.value = hcId;
            form.appendChild(hcInput);

            // Add CSRF token if needed
            const csrfTokenInput = document.querySelector('input[name="csrf_token"]');
            if (csrfTokenInput) {
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrf_token';
                csrfInput.value = csrfTokenInput.value;
                form.appendChild(csrfInput);
            }

            // Submit the form
            document.body.appendChild(form);
            form.submit();
        });
    });
});
