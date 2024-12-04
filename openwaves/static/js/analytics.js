document.addEventListener('DOMContentLoaded', function() {
    // Handle pool selection change to auto-submit the form
    const poolSelect = document.getElementById('pool');
    if (poolSelect) {
        poolSelect.addEventListener('change', function() {
            this.form.submit();
        });
    }

    // Toggle function for question detail rows
    function toggleDetail(questionId) {
        const detailRow = document.getElementById(`details-${questionId}`);
        if (detailRow) {
            detailRow.classList.toggle('is-hidden');
        }
    }

    // Attach click event to each question row
    document.querySelectorAll('.question-row').forEach(row => {
        const questionId = row.getAttribute('data-question-id');
        row.addEventListener('click', () => toggleDetail(questionId));
    });
});
