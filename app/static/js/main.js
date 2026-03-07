// Funciones globales

// Confirmar eliminación
function confirmDelete(message) {
    return confirm(message || '¿Estás seguro de eliminar este elemento?');
}

// Formatear precios
document.addEventListener('DOMContentLoaded', function() {
    // Auto-cerrar alertas
    setTimeout(function() {
        document.querySelectorAll('.alert-dismissible').forEach(function(alert) {
            let closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) closeBtn.click();
        });
    }, 5000);
});

// Peticiones AJAX
async function fetchAPI(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: { 'Content-Type': 'application/json' }
    };
    
    if (data) options.body = JSON.stringify(data);
    
    try {
        const response = await fetch(url, options);
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        return { success: false, error: error.message };
    }
}