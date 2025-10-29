// Transaction History Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Add click handler to entire card
    const cards = document.querySelectorAll('.transaction-card-modern');
    cards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Don't trigger if clicking the actual link
            if (e.target.closest('.btn-view-transaction')) return;
            
            const link = this.querySelector('.btn-view-transaction');
            if (link) {
                link.click();
            }
        });
    });
    
    // Add ripple effect on click
    cards.forEach(card => {
        card.addEventListener('mousedown', function(e) {
            const ripple = document.createElement('div');
            ripple.style.position = 'absolute';
            ripple.style.borderRadius = '50%';
            ripple.style.background = 'rgba(102, 126, 234, 0.3)';
            ripple.style.width = ripple.style.height = '100px';
            ripple.style.left = e.clientX - this.offsetLeft - 50 + 'px';
            ripple.style.top = e.clientY - this.offsetTop - 50 + 'px';
            ripple.style.animation = 'ripple 0.6s ease-out';
            ripple.style.pointerEvents = 'none';
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
});

// Add ripple animation dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        from {
            transform: scale(0);
            opacity: 1;
        }
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
