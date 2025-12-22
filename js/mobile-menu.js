/* ===== MOBILE MENU TOGGLE FUNCTIONALITY ===== */
(function() {
    'use strict';
    
    // Initialize mobile menu
    function initMobileMenu() {
        const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
        const mobileMenu = document.querySelector('.mobile-menu');
        const mobileMenuClose = document.querySelector('.mobile-menu-close');
        const body = document.body;
        
        if (!mobileMenuToggle || !mobileMenu) {
            return;
        }
        
        // Toggle menu
        mobileMenuToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            mobileMenu.classList.add('active');
            body.style.overflow = 'hidden';
        });
        
        // Close menu
        if (mobileMenuClose) {
            mobileMenuClose.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                mobileMenu.classList.remove('active');
                body.style.overflow = '';
            });
        }
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (mobileMenu.classList.contains('active') && 
                !mobileMenu.contains(e.target) && 
                !mobileMenuToggle.contains(e.target)) {
                mobileMenu.classList.remove('active');
                body.style.overflow = '';
            }
        });
        
        // Close menu on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && mobileMenu.classList.contains('active')) {
                mobileMenu.classList.remove('active');
                body.style.overflow = '';
            }
        });
        
        // Close menu when clicking a link
        const menuLinks = mobileMenu.querySelectorAll('a');
        menuLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                mobileMenu.classList.remove('active');
                body.style.overflow = '';
            });
        });
    }
    
    // Initialize admin sidebar toggle
    function initAdminSidebar() {
        const sidebarToggle = document.querySelector('.admin-sidebar-toggle');
        const adminSidebar = document.querySelector('.admin-sidebar');
        
        if (!sidebarToggle || !adminSidebar) {
            return;
        }
        
        sidebarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            adminSidebar.classList.toggle('active');
        });
        
        // Close sidebar when clicking outside
        document.addEventListener('click', function(e) {
            if (adminSidebar.classList.contains('active') && 
                !adminSidebar.contains(e.target) && 
                !sidebarToggle.contains(e.target)) {
                adminSidebar.classList.remove('active');
            }
        });
    }
    
    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initMobileMenu();
            initAdminSidebar();
        });
    } else {
        initMobileMenu();
        initAdminSidebar();
    }
})();

