// Main JavaScript file for the application
document.addEventListener('DOMContentLoaded', function() {
    // Form submission handling
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(form);
            try {
                const response = await fetch(form.action, {
                    method: form.method,
                    body: formData,
                    credentials: 'same-origin'
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    if (form.id === 'loginForm' || form.id === 'registerForm') {
                        window.location.href = '/home';
                    } else {
                        // Show success message
                        alert(data.message || 'Operation successful');
                        location.reload();
                    }
                } else {
                    throw new Error(data.detail || 'Something went wrong');
                }
            } catch (error) {
                // Show error message
                const errorDiv = document.querySelector('.error-message');
                if (errorDiv) {
                    errorDiv.textContent = error.message;
                    errorDiv.style.display = 'block';
                } else {
                    alert(error.message);
                }
            }
        });
    });
});
