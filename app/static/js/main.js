// Main JavaScript for Escalas application

console.log('Escalas application loaded');

// Toast notification function
function showToast(message, type = 'success') {
    const toastHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const container = document.querySelector('main');
    if (container) {
        container.insertAdjacentHTML('afterbegin', toastHtml);
    }
}

// API error handler
function handleApiError(error) {
    console.error('API Error:', error);
    showToast('Erro ao processar requisição', 'danger');
}

// Format date to DD/MM/YYYY
function formatDate(date) {
    if (typeof date === 'string') return date;
    const d = new Date(date);
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const year = d.getFullYear();
    return `${day}/${month}/${year}`;
}

// Parse date from DD/MM/YYYY to Date object
function parseDate(dateStr) {
    const [day, month, year] = dateStr.split('/');
    return new Date(year, month - 1, day);
}

// Initialize Bootstrap tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
