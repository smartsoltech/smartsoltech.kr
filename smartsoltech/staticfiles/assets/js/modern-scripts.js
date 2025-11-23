// Modern Scripts for SmartSolTech Website
document.addEventListener('DOMContentLoaded', function() {
    
    // Hide loading screen
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
        setTimeout(() => {
            loadingScreen.style.opacity = '0';
            setTimeout(() => {
                loadingScreen.style.display = 'none';
            }, 300);
        }, 1000);
    }
    
    // Theme Toggle Functionality
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;
    
    // Check for saved theme preference
    const currentTheme = localStorage.getItem('theme') || 'light';
    html.setAttribute('data-theme', currentTheme);
    updateThemeIcon(currentTheme);
    
    themeToggle.addEventListener('click', function() {
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
        
        // Add animation
        this.style.transform = 'scale(0.8)';
        setTimeout(() => {
            this.style.transform = 'scale(1)';
        }, 150);
    });
    
    function updateThemeIcon(theme) {
        const icon = themeToggle.querySelector('i');
        if (theme === 'dark') {
            icon.className = 'fas fa-sun';
            themeToggle.setAttribute('aria-label', 'Переключить на светлую тему');
        } else {
            icon.className = 'fas fa-moon';
            themeToggle.setAttribute('aria-label', 'Переключить на темную тему');
        }
    }
    
    // Navbar scroll behavior
    const navbar = document.querySelector('.navbar-modern');
    let lastScrollTop = 0;
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // Add/remove scrolled class
        if (scrollTop > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        
        // Hide/show navbar on scroll
        if (scrollTop > lastScrollTop && scrollTop > 100) {
            navbar.style.transform = 'translateY(-100%)';
        } else {
            navbar.style.transform = 'translateY(0)';
        }
        
        lastScrollTop = scrollTop;
    });
    
    // Scroll to top button
    const scrollToTopBtn = document.getElementById('scroll-to-top');
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollToTopBtn.style.display = 'block';
            scrollToTopBtn.style.opacity = '1';
        } else {
            scrollToTopBtn.style.opacity = '0';
            setTimeout(() => {
                if (window.pageYOffset <= 300) {
                    scrollToTopBtn.style.display = 'none';
                }
            }, 300);
        }
    });
    
    scrollToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const offsetTop = target.offsetTop - 80; // Account for fixed navbar
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in-up');
                // Add stagger delay for child elements
                const children = entry.target.querySelectorAll('.service-card, .feature-list > *, .step-card');
                children.forEach((child, index) => {
                    setTimeout(() => {
                        child.classList.add('animate-fade-in-up');
                    }, index * 100);
                });
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.service-card, .card-modern, .step-card').forEach(el => {
        observer.observe(el);
    });
    
    // Form enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalContent = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Отправляем...';
                submitBtn.disabled = true;
                
                // Re-enable after 3 seconds (in case of slow response)
                setTimeout(() => {
                    submitBtn.innerHTML = originalContent;
                    submitBtn.disabled = false;
                }, 3000);
            }
        });
    });
    
    // Parallax effect for hero section
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.animate-float');
        
        parallaxElements.forEach(element => {
            const speed = 0.5;
            element.style.transform = `translateY(${scrolled * speed}px)`;
        });
    });
    
    // Service cards hover effect
    document.querySelectorAll('.service-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Card modern hover effects
    document.querySelectorAll('.card-modern').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 25px 50px -12px rgba(0, 0, 0, 0.25)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.boxShadow = 'var(--shadow)';
        });
    });
    
    // Add loading animation to buttons
    document.querySelectorAll('.btn-primary-modern, .btn-secondary-modern').forEach(btn => {
        btn.addEventListener('click', function(e) {
            // Create ripple effect
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.4);
                transform: scale(0);
                animation: ripple 0.6s linear;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Typing animation for hero text (optional)
    const typingText = document.querySelector('.typing-text');
    if (typingText) {
        const text = typingText.textContent;
        typingText.textContent = '';
        let i = 0;
        
        function typeWriter() {
            if (i < text.length) {
                typingText.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            }
        }
        
        setTimeout(typeWriter, 1000);
    }
    
    // Mobile menu enhancements
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            
            // Animate the toggler icon
            this.style.transform = 'rotate(180deg)';
            setTimeout(() => {
                this.style.transform = 'rotate(0deg)';
            }, 300);
        });
        
        // Close menu when clicking on a link
        document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
            link.addEventListener('click', () => {
                const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                    hide: true
                });
            });
        });
    }
    
    // Newsletter form
    const newsletterForm = document.querySelector('footer form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = this.querySelector('input[type="email"]').value;
            
            if (email) {
                // Show success message
                const button = this.querySelector('button');
                const originalContent = button.innerHTML;
                button.innerHTML = '<i class="fas fa-check"></i>';
                button.style.background = '#10b981';
                
                setTimeout(() => {
                    button.innerHTML = originalContent;
                    button.style.background = '';
                    this.reset();
                }, 2000);
            }
        });
    }
});

// Add CSS for ripple animation
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(2);
            opacity: 0;
        }
    }
    
    .animate-fade-in-up {
        opacity: 1 !important;
        transform: translateY(0) !important;
    }
    
    /* Smooth transitions */
    .navbar-modern {
        transition: transform 0.3s ease, background-color 0.3s ease;
    }
    
    .service-card, .card-modern {
        opacity: 0;
        transform: translateY(30px);
        transition: all 0.6s ease;
    }
    
    .step-card {
        opacity: 0;
        transform: translateX(-30px);
        transition: all 0.6s ease;
    }
    
    .step-card:nth-child(even) {
        transform: translateX(30px);
    }
`;
document.head.appendChild(style);