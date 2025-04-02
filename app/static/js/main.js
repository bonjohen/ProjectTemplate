// Main JavaScript file for the application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            // Add fade class
            alert.classList.add('fade');

            // Remove element after animation completes
            setTimeout(function() {
                if (alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }, 500);
        }, 5000);
    });

    // Add active class to current nav item
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');

    navLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');

            // If in dropdown, also activate parent
            const dropdownParent = link.closest('.dropdown');
            if (dropdownParent) {
                const dropdownToggle = dropdownParent.querySelector('.dropdown-toggle');
                if (dropdownToggle) {
                    dropdownToggle.classList.add('active');
                }
            }
        }
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');

    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();

                // Show validation messages
                const invalidFields = form.querySelectorAll(':invalid');
                invalidFields.forEach(field => {
                    // Add shake animation to invalid fields
                    field.classList.add('shake');
                    setTimeout(() => {
                        field.classList.remove('shake');
                    }, 600);
                });

                // Scroll to first invalid field
                if (invalidFields.length > 0) {
                    invalidFields[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
                    invalidFields[0].focus();
                }
            }

            form.classList.add('was-validated');
        }, false);
    });

    // Add loading spinner for form submissions and link clicks
    const submitButtons = document.querySelectorAll('button[type="submit"]:not(.no-spinner)');
    const spinnerLinks = document.querySelectorAll('a.spinner-link');
    const spinnerOverlay = document.createElement('div');

    spinnerOverlay.className = 'spinner-overlay';
    spinnerOverlay.innerHTML = '<div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div>';
    document.body.appendChild(spinnerOverlay);

    submitButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const form = this.closest('form');
            if (form && form.checkValidity()) {
                spinnerOverlay.classList.add('show');

                // Store original text and disable button
                this.dataset.originalText = this.innerHTML;
                this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
                this.disabled = true;
            }
        });
    });

    spinnerLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            spinnerOverlay.classList.add('show');
        });
    });

    // Add animation to elements when they come into view
    const animateElements = document.querySelectorAll('.animate-on-scroll');

    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1
        });

        animateElements.forEach(element => {
            observer.observe(element);
        });
    } else {
        // Fallback for browsers that don't support IntersectionObserver
        animateElements.forEach(element => {
            element.classList.add('fade-in');
        });
    }

    // Character counter for textareas
    const textareas = document.querySelectorAll('textarea[maxlength]');

    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        const counterDiv = document.createElement('div');
        counterDiv.className = 'form-text text-end';
        counterDiv.innerHTML = `<span class="char-count">${textarea.value.length}</span>/${maxLength}`;

        textarea.parentNode.insertBefore(counterDiv, textarea.nextSibling);

        textarea.addEventListener('input', function() {
            const currentLength = this.value.length;
            const counter = this.parentNode.querySelector('.char-count');
            counter.textContent = currentLength;

            // Change color when approaching limit
            if (currentLength > maxLength * 0.9) {
                counter.classList.add('text-danger');
            } else {
                counter.classList.remove('text-danger');
            }
        });
    });
});
