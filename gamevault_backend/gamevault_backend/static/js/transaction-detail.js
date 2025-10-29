// Transaction Detail Page JavaScript

// CSRF token helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// Copy key to clipboard with animation
function copyKey(key, itemId) {
    navigator.clipboard.writeText(key).then(() => {
        const btn = event.target.closest('.btn-copy');
        const keyCode = document.getElementById(`key-${itemId}`);
        
        // Animate button
        btn.classList.add('copied');
        
        // Animate key code
        keyCode.style.transition = 'all 0.3s ease';
        keyCode.style.background = '#d4edda';
        keyCode.style.borderColor = '#28a745';
        
        // Show success message
        const statusDiv = document.getElementById(`status-${itemId}`);
        statusDiv.className = 'status-message success';
        statusDiv.textContent = '✓ Key copied to clipboard!';
        
        // Reset after delay
        setTimeout(() => {
            btn.classList.remove('copied');
            keyCode.style.background = 'white';
            keyCode.style.borderColor = '#667eea';
            statusDiv.style.display = 'none';
        }, 2000);
    }).catch(err => {
        console.error('Copy failed:', err);
        const statusDiv = document.getElementById(`status-${itemId}`);
        statusDiv.className = 'status-message error';
        statusDiv.textContent = '✗ Failed to copy. Please copy manually.';
    });
}

// Send key via email with loading state
async function sendKey(btn) {
    const itemId = btn.dataset.itemId;
    const transactionId = btn.dataset.transactionId;
    const statusDiv = document.getElementById(`status-${itemId}`);
    
    // Disable button and show loading
    btn.disabled = true;
    const originalHTML = btn.innerHTML;
    btn.innerHTML = `
        <svg width="16" height="16" fill="currentColor" class="spinning">
            <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="31.4" stroke-dashoffset="10"/>
        </svg>
        <span>Sending...</span>
    `;
    
    // Hide previous messages
    statusDiv.style.display = 'none';
    
    try {
        const response = await fetch(
            `/store/transactions/${transactionId}/items/${itemId}/send-key/`,
            {
                method: 'POST',
                headers: { 'X-CSRFToken': csrftoken }
            }
        );
        
        const data = await response.json();
        
        if (data.success) {
            statusDiv.className = 'status-message success';
            statusDiv.textContent = `✓ ${data.message}`;
            btn.classList.add('btn-sent');
            btn.innerHTML = `
                <svg width="16" height="16" fill="currentColor">
                    <circle cx="8" cy="8" r="7" fill="#28a745"/>
                    <path d="M4 8 L7 11 L12 6" stroke="white" stroke-width="2" fill="none"/>
                </svg>
                <span>Key Sent</span>
            `;
            
            // Reload after delay
            setTimeout(() => window.location.reload(), 3000);
        } else {
            throw new Error(data.error || 'Failed to send');
        }
    } catch (error) {
        statusDiv.className = 'status-message error';
        statusDiv.textContent = `✗ ${error.message}`;
        btn.disabled = false;
        btn.innerHTML = originalHTML;
    }
}

// Add spinning animation for loading state
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .spinning {
        animation: spin 1s linear infinite;
    }
`;
document.head.appendChild(style);
