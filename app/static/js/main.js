// Main JavaScript file for the application

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    // Get all alert elements
    const alerts = document.querySelectorAll('.alert');
    
    // Set timeout to fade out and remove each alert
    alerts.forEach(function(alert) {
        setTimeout(function() {
            // Add fade class
            alert.classList.add('fade');
            
            // Remove element after animation completes
            setTimeout(function() {
                alert.remove();
            }, 500);
        }, 5000);
    });
    
    // Add active class to current nav item
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        }
    });
});
