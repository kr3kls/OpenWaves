/**
 * File: navbar.test.js
 * 
 * Description: This file contains tests for the navbar functionality.
 * 
 * @jest-environment jsdom
 */

require('../openwaves/static/js/navbar'); // This will execute the navbar.js code, including the DOMContentLoaded event

describe('Navbar functionality', () => {
    let navbarBurger, navbarMenu;

    beforeEach(() => {
        // Set up the DOM with a navbar-burger and navbar-menu
        document.body.innerHTML = `
            <nav class="navbar">
                <div class="navbar-burger" data-target="navbarMenu" aria-expanded="false"></div>
                <div id="navbarMenu" class="navbar-menu"></div>
            </nav>
        `;

        navbarBurger = document.querySelector('.navbar-burger');
        navbarMenu = document.getElementById('navbarMenu');

        // Simulate DOMContentLoaded to initialize the event listeners in navbar.js
        document.dispatchEvent(new Event('DOMContentLoaded'));
    });

    /**
     * Test ID: UT-113
     * 
     * This test ensures that clicking the `navbar-burger` element toggles the "is-active" class
     * on both the `navbar-burger` and `navbar-menu` elements, thereby showing or hiding the menu.
     * 
     * Asserts:
     * - The "is-active" class is added to both elements after the first click.
     * - The "is-active" class is removed from both elements after the second click.
     */
    test('click event on navbar-burger toggles "is-active" class on both elements', () => {
        // Simulate the click event on the navbar-burger
        navbarBurger.click();

        // Check if the "is-active" class has been added to both elements
        expect(navbarBurger.classList.contains('is-active')).toBe(true);
        expect(navbarMenu.classList.contains('is-active')).toBe(true);

        // Simulate another click to toggle off
        navbarBurger.click();

        // Check if the "is-active" class has been removed from both elements
        expect(navbarBurger.classList.contains('is-active')).toBe(false);
        expect(navbarMenu.classList.contains('is-active')).toBe(false);
    });

    /**
     * Test ID: UT-114
     * 
     * This test ensures that pressing the "Enter" key when focused on the `navbar-burger` element
     * toggles the "is-active" class on both the `navbar-burger` and `navbar-menu` elements, 
     * thereby showing or hiding the menu.
     * 
     * Asserts:
     * - The "is-active" class is added to both elements after the first "Enter" keydown event.
     * - The "is-active" class is removed from both elements after the second "Enter" keydown event.
     */
    test('keydown event with "Enter" key toggles "is-active" class on both elements', () => {
        // Create and dispatch a keydown event with the "Enter" key
        const enterEvent = new KeyboardEvent('keydown', { key: 'Enter' });
        navbarBurger.dispatchEvent(enterEvent);

        // Check if the "is-active" class has been added to both elements
        expect(navbarBurger.classList.contains('is-active')).toBe(true);
        expect(navbarMenu.classList.contains('is-active')).toBe(true);

        // Dispatch another "Enter" keydown event to toggle off
        navbarBurger.dispatchEvent(enterEvent);

        // Check if the "is-active" class has been removed from both elements
        expect(navbarBurger.classList.contains('is-active')).toBe(false);
        expect(navbarMenu.classList.contains('is-active')).toBe(false);
    });

    /**
     * Test ID: UT-115
     * 
     * This test ensures that pressing the "Space" key when focused on the `navbar-burger` element
     * toggles the "is-active" class on both the `navbar-burger` and `navbar-menu` elements, 
     * thereby showing or hiding the menu.
     * 
     * Asserts:
     * - The "is-active" class is added to both elements after the first "Space" keydown event.
     * - The "is-active" class is removed from both elements after the second "Space" keydown event.
     */
    test('keydown event with "Space" key toggles "is-active" class on both elements', () => {
        // Create and dispatch a keydown event with the "Space" key
        const spaceEvent = new KeyboardEvent('keydown', { key: ' ' });
        navbarBurger.dispatchEvent(spaceEvent);

        // Check if the "is-active" class has been added to both elements
        expect(navbarBurger.classList.contains('is-active')).toBe(true);
        expect(navbarMenu.classList.contains('is-active')).toBe(true);

        // Dispatch another "Space" keydown event to toggle off
        navbarBurger.dispatchEvent(spaceEvent);

        // Check if the "is-active" class has been removed from both elements
        expect(navbarBurger.classList.contains('is-active')).toBe(false);
        expect(navbarMenu.classList.contains('is-active')).toBe(false);
    });

    /**
     * Test ID: UT-116
     * 
     * Test that pressing irrelevant keys does not trigger the `toggleMenu` function.
     * 
     * This test ensures that the `toggleMenu` function is not called when keys other than
     * "Enter" or "Space" are pressed on the `navbar-burger` element, such as the "Escape" key.
     * 
     * Asserts:
     * - `toggleMenu` is not called when an irrelevant key ("Escape") is pressed.
     */
    test('keydown event with irrelevant keys does not call toggleMenu', () => {
        const toggleMenuSpy = jest.spyOn(window, 'toggleMenu');

        const event = new KeyboardEvent('keydown', { key: 'Escape' });
        navbarBurger.dispatchEvent(event);

        expect(toggleMenuSpy).not.toHaveBeenCalled();

        toggleMenuSpy.mockRestore();
    });

    /**
     * Test ID: UT-117
     * 
     * Test that multiple `navbar-burger` elements toggle their respective menus independently.
     * 
     * This test ensures that each `navbar-burger` element can independently control its corresponding 
     * `navbar-menu` without affecting the other menus. When one `navbar-burger` is clicked, 
     * only its corresponding menu should toggle.
     * 
     * Asserts:
     * - Clicking the first `navbar-burger` adds the "is-active" class to itself and its corresponding menu.
     * - The second `navbar-burger` and menu remain unaffected until explicitly toggled.
     * - Both menus can be toggled independently.
     */
    test('multiple navbar-burger elements toggle their respective menus independently', () => {
        // Set up the DOM with multiple navbar-burgers
        document.body.innerHTML = `
            <nav class="navbar">
                <div class="navbar-burger" data-target="navbarMenu1" aria-expanded="false"></div>
                <div id="navbarMenu1" class="navbar-menu"></div>
                <div class="navbar-burger" data-target="navbarMenu2" aria-expanded="false"></div>
                <div id="navbarMenu2" class="navbar-menu"></div>
            </nav>
        `;

        const navbarBurgers = document.querySelectorAll('.navbar-burger');
        const navbarMenus = document.querySelectorAll('.navbar-menu');

        // Simulate DOMContentLoaded event to initialize the navbar
        document.dispatchEvent(new Event('DOMContentLoaded'));

        // Click the first navbar-burger
        navbarBurgers[0].click();

        expect(navbarBurgers[0].classList.contains('is-active')).toBe(true);
        expect(navbarMenus[0].classList.contains('is-active')).toBe(true);

        // Ensure the second navbar-burger and menu are unaffected
        expect(navbarBurgers[1].classList.contains('is-active')).toBe(false);
        expect(navbarMenus[1].classList.contains('is-active')).toBe(false);

        // Click the second navbar-burger
        navbarBurgers[1].click();

        expect(navbarBurgers[1].classList.contains('is-active')).toBe(true);
        expect(navbarMenus[1].classList.contains('is-active')).toBe(true);

        // Both menus should now be active
        expect(navbarMenus[0].classList.contains('is-active')).toBe(true);
        expect(navbarMenus[1].classList.contains('is-active')).toBe(true);
    });

    /**
     * Test ID: UT-118
     * 
     * Test that `toggleMenu` handles a missing `data-target` attribute gracefully.
     * 
     * This test ensures that when a `navbar-burger` element without a `data-target` attribute is clicked,
     * the `toggleMenu` function does not throw an error, and an appropriate console error message is logged.
     * 
     * Asserts:
     * - Clicking a `navbar-burger` without a `data-target` does not throw an error.
     * - A console error is logged with the message indicating that the target element was not found.
     */
    test('toggleMenu handles missing data-target gracefully', () => {
        // Set up the DOM with a navbar-burger missing data-target
        document.body.innerHTML = `
            <nav class="navbar">
                <div class="navbar-burger" aria-expanded="false"></div>
            </nav>
        `;
    
        const navbarBurger = document.querySelector('.navbar-burger');
    
        // Spy on console.error
        const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
        // Simulate DOMContentLoaded event to initialize the navbar
        document.dispatchEvent(new Event('DOMContentLoaded'));
    
        // Try to click the navbar-burger
        expect(() => {
            navbarBurger.click();
        }).not.toThrow();
    
        // Assert that console.error was called with the correct message
        expect(consoleSpy).toHaveBeenCalledWith(
            'toggleMenu: Target element with id "undefined" not found.'
        );
    
        // Clean up
        consoleSpy.mockRestore();
    });    

    /**
     * Test ID: UT-119
     * Test the `toggleMenu` function when the target element does not exist.
     *
     * This test ensures that the `toggleMenu` function handles cases where the target element
     * does not exist and logs an appropriate error message without throwing an exception.
     *
     * Asserts:
     * - Clicking the `navbar-burger` does not throw an error.
     * - A specific error message is logged to the console.
     */
    test('toggleMenu handles non-existent target element gracefully', () => {
        // Set up the DOM with a navbar-burger pointing to a non-existent target
        document.body.innerHTML = `
            <nav class="navbar">
                <div class="navbar-burger" data-target="nonExistentMenu" aria-expanded="false"></div>
            </nav>
        `;
    
        const navbarBurger = document.querySelector('.navbar-burger');
    
        // Spy on console.error
        const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
        // Simulate DOMContentLoaded event to initialize the navbar
        document.dispatchEvent(new Event('DOMContentLoaded'));
    
        // Try to click the navbar-burger
        expect(() => {
            navbarBurger.click();
        }).not.toThrow();
    
        // Assert that console.error was called with the correct message
        expect(consoleSpy).toHaveBeenCalledWith(
            'toggleMenu: Target element with id "nonExistentMenu" not found.'
        );
    
        // Clean up
        consoleSpy.mockRestore();
    });    

    /**
     * Test ID: UT-120
     * Test the `initializeNavbar` function when there are no `navbar-burger` elements in the DOM.
     *
     * This test ensures that the `initializeNavbar` function gracefully handles the absence of 
     * `navbar-burger` elements without causing errors.
     *
     * Asserts:
     * - The `document.querySelectorAll` is called to search for `navbar-burger` elements.
     */
    test('initializeNavbar handles absence of navbar-burger elements gracefully', () => {
        // Set up the DOM without any navbar-burger elements
        document.body.innerHTML = `
            <nav class="navbar">
                <!-- No navbar-burger elements -->
            </nav>
        `;

        // Spy on document.querySelectorAll
        const querySelectorAllSpy = jest.spyOn(document, 'querySelectorAll');

        // Simulate DOMContentLoaded event to initialize the navbar
        document.dispatchEvent(new Event('DOMContentLoaded'));

        // Ensure querySelectorAll was called
        expect(querySelectorAllSpy).toHaveBeenCalledWith('.navbar-burger');

        // Clean up
        querySelectorAllSpy.mockRestore();
    });

    /**
     * Test ID: UT-121
     * Test the `toggleMenu` function's behavior on the `aria-expanded` attribute of `navbar-burger`.
     *
     * This test ensures that the `toggleMenu` function toggles the `aria-expanded` attribute
     * of the `navbar-burger` element between `"true"` and `"false"` correctly.
     *
     * Asserts:
     * - The `aria-expanded` attribute is `"false"` initially.
     * - The `aria-expanded` attribute changes to `"true"` after the first toggle.
     * - The `aria-expanded` attribute changes back to `"false"` after the second toggle.
     */
    test('toggleMenu toggles aria-expanded attribute correctly', () => {
        // Initial state
        expect(navbarBurger.getAttribute('aria-expanded')).toBe('false');

        // First toggle
        window.toggleMenu(navbarBurger);
        expect(navbarBurger.getAttribute('aria-expanded')).toBe('true');

        // Second toggle
        window.toggleMenu(navbarBurger);
        expect(navbarBurger.getAttribute('aria-expanded')).toBe('false');
    });

    /**
     * Test ID: UT-122
     * Test the attachment of event listeners to `navbar-burger` elements.
     *
     * This test ensures that the `initializeNavbar` function correctly attaches 
     * event listeners (`click` and `keydown`) to each `navbar-burger` element in the DOM.
     *
     * Asserts:
     * - The `addEventListener` method is called for both `click` and `keydown` events.
     */
    test('event listeners are attached to navbar-burger elements', () => {
        // Spy on addEventListener
        const addEventListenerSpy = jest.spyOn(Element.prototype, 'addEventListener');

        // Simulate DOMContentLoaded event to initialize the navbar
        document.dispatchEvent(new Event('DOMContentLoaded'));

        // Expect addEventListener to be called for 'click' and 'keydown' events
        expect(addEventListenerSpy).toHaveBeenCalledWith('click', expect.any(Function));
        expect(addEventListenerSpy).toHaveBeenCalledWith('keydown', expect.any(Function));

        // Clean up
        addEventListenerSpy.mockRestore();
    });
});
