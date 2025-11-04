// Huvudsaklig JavaScript för Tidrapporteringssystem

document.addEventListener('DOMContentLoaded', function() {
    // Initialisera tooltips
    initializeTooltips();
    
    // Initialisera datum inputs
    initializeDateInputs();
    
    // Lägg till animationer
    addPageAnimations();
    
    // Auto-save för formulär
    initializeAutoSave();
    
    // Responsiv navigation
    initializeResponsiveNav();
    
    console.log('Tidrapporteringssystem initierat');
});

// Initialisera Bootstrap tooltips
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialisera datum inputs med dagens datum
function initializeDateInputs() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    
    dateInputs.forEach(input => {
        if (!input.value) {
            input.value = today;
        }
    });
}

// Lägg till sida-animationer
function addPageAnimations() {
    // Fade in för kort
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// Auto-save funktionalitet för formulär
function initializeAutoSave() {
    const forms = document.querySelectorAll('form[data-autosave]');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                saveFormData(form);
            });
        });
        
        // Ladda sparad data
        loadFormData(form);
    });
}

// Spara formulärdata i localStorage
function saveFormData(form) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    const formId = form.id || form.className;
    localStorage.setItem(`autosave_${formId}`, JSON.stringify(data));
    
    // Visa sparad indikator
    showSaveIndicator(form);
}

// Ladda formulärdata från localStorage
function loadFormData(form) {
    const formId = form.id || form.className;
    const savedData = localStorage.getItem(`autosave_${formId}`);
    
    if (savedData) {
        const data = JSON.parse(savedData);
        
        Object.keys(data).forEach(key => {
            const input = form.querySelector(`[name="${key}"]`);
            if (input && input.type !== 'submit') {
                input.value = data[key];
            }
        });
    }
}

// Visa sparad indikator
function showSaveIndicator(form) {
    let indicator = form.querySelector('.save-indicator');
    
    if (!indicator) {
        indicator = document.createElement('small');
        indicator.className = 'save-indicator text-success';
        indicator.innerHTML = '<i class="fas fa-check me-1"></i>Autosparad';
        form.appendChild(indicator);
    }
    
    indicator.style.opacity = '1';
    
    setTimeout(() => {
        indicator.style.opacity = '0';
    }, 2000);
}

// Responsiv navigation
function initializeResponsiveNav() {
    const navbar = document.querySelector('.navbar');
    const navbarToggler = document.querySelector('.navbar-toggler');
    
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            navbar.classList.toggle('expanded');
        });
    }
}

// Utility funktioner

// Formattera tid (timmar)
function formatHours(hours) {
    return parseFloat(hours).toFixed(1) + 'h';
}

// Formattera datum
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('sv-SE');
}

// Validera email
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Visa laddningsindikator
function showLoading(element) {
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    element.appendChild(spinner);
}

// Göm laddningsindikator
function hideLoading(element) {
    const spinner = element.querySelector('.spinner');
    if (spinner) {
        spinner.remove();
    }
}

// Toast notifikationer
function showToast(message, type = 'info') {
    const toastContainer = getOrCreateToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Ta bort toast efter att den stängs
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Hämta eller skapa toast container
function getOrCreateToastContainer() {
    let container = document.querySelector('.toast-container');
    
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }
    
    return container;
}

// Bekräfta dialoger
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Debounce funktion för sök
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Filtrera tabell
function filterTable(tableId, searchQuery) {
    const table = document.getElementById(tableId);
    const rows = table.querySelectorAll('tbody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const match = text.includes(searchQuery.toLowerCase());
        row.style.display = match ? '' : 'none';
    });
}

// Exportera data till CSV
function exportTableToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    const rows = Array.from(table.querySelectorAll('tr:not([style*="display: none"])'));
    
    let csv = '';
    
    rows.forEach(row => {
        const cells = Array.from(row.cells);
        const rowData = cells.map(cell => {
            // Rensa bort HTML och escape quotes
            const text = cell.textContent.replace(/"/g, '""');
            return `"${text}"`;
        }).join(',');
        
        csv += rowData + '\n';
    });
    
    downloadCSV(csv, filename);
}

// Ladda ner CSV
function downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Lokalisering av datum
function getWeekNumber(date) {
    const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
    const dayNum = d.getUTCDay() || 7;
    d.setUTCDate(d.getUTCDate() + 4 - dayNum);
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
    return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
}

// Räkna arbetsdagar mellan två datum
function getWorkDays(startDate, endDate) {
    let count = 0;
    const curDate = new Date(startDate);
    
    while (curDate <= endDate) {
        const dayOfWeek = curDate.getDay();
        if (dayOfWeek !== 0 && dayOfWeek !== 6) {
            count++;
        }
        curDate.setDate(curDate.getDate() + 1);
    }
    
    return count;
}

// Lokalt API-wrapper för AJAX-anrop
const API = {
    async get(url) {
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('API GET error:', error);
            showToast('Ett fel uppstod vid hämtning av data', 'danger');
            throw error;
        }
    },
    
    async post(url, data) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('API POST error:', error);
            showToast('Ett fel uppstod vid skickning av data', 'danger');
            throw error;
        }
    }
};

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl + S för att spara formulär
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            if (form.checkValidity()) {
                form.submit();
            }
        });
    }
    
    // Esc för att stänga modaler
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) bsModal.hide();
        });
    }
});

// Performance monitoring (för utveckling)
if (typeof performance !== 'undefined') {
    window.addEventListener('load', function() {
        setTimeout(function() {
            const perfData = performance.getEntriesByType('navigation')[0];
            console.log('Sidladdningstid:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
        }, 0);
    });
}