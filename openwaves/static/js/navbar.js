/*
*   File: navbar.js
*
*   Description: This file contains the JavaScript code to toggle the navbar menu.
*/



// Function to toggle the menu
function toggleMenu($el) {
    // Get the target from the "data-target" attribute
    const target = $el.dataset.target;
    const $target = document.getElementById(target);

    // Check if $target exists
    if ($target) {
        // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
        $el.classList.toggle('is-active');
        $target.classList.toggle('is-active');

        // Update aria-expanded attribute for accessibility
        const isExpanded = $el.getAttribute('aria-expanded') === 'true';
        $el.setAttribute('aria-expanded', !isExpanded);
    } else {
        // Handle the case where $target is null
        console.error(`toggleMenu: Target element with id "${target}" not found.`);
    }
}

// Expose toggleMenu for testing
window.toggleMenu = toggleMenu;

document.addEventListener('DOMContentLoaded', function () {
    // Get all "navbar-burger" elements
    const $navbarBurgers = Array.prototype.slice.call(
        document.querySelectorAll('.navbar-burger'),
        0
    );

    // Check if there are any navbar burgers
    if ($navbarBurgers.length > 0) {
        // Add event listeners on each navbar burger element
        $navbarBurgers.forEach(function ($el) {
            // Add click event
            $el.addEventListener('click', function () {
                toggleMenu($el); // Now refers to the global toggleMenu
            });

            // Add keydown event for accessibility (Enter or Space keys)
            $el.addEventListener('keydown', function (event) {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault(); // Prevent default action (e.g., scrolling)
                    toggleMenu($el); // Now refers to the global toggleMenu
                }
            });
        });
    }
});
