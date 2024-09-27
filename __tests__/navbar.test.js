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

    test('keydown event with irrelevant keys does not call toggleMenu', () => {
        const toggleMenuSpy = jest.spyOn(window, 'toggleMenu');

        const event = new KeyboardEvent('keydown', { key: 'Escape' });
        navbarBurger.dispatchEvent(event);

        expect(toggleMenuSpy).not.toHaveBeenCalled();

        toggleMenuSpy.mockRestore();
    });

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
