// Payment Status Page Script
const API_BASE_URL = 'https://brandotpofficial.onrender.com';

let orderId = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('💳 Payment status page loaded');
    
    // Extract order ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    orderId = urlParams.get('orderid');
    
    if (!orderId) {
        showError('No order ID found. Redirecting to wallet...');
        setTimeout(() => {
            window.location.href = 'wallet.html';
        }, 3000);
        return;
    }
    
    console.log('✅ Order ID:', orderId);
    
    // Check payment status
    checkStatus();
});

// Check payment status from backend
async function checkStatus() {
    try {
        const token = localStorage.getItem('access_token');
        
        if (!token) {
            showError('Not authenticated. Redirecting to login...');
            setTimeout(() => {
                window.location.href = 'auth.html';
            }, 2000);
            return;
        }
        
        console.log('🔄 Checking payment status for order:', orderId);
        
        const response = await fetch(`${API_BASE_URL}/api/payments/check-status?order_id=${orderId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        console.log('📊 Status response:', result);
        
        if (result.status === 'SUCCESS') {
            showSuccess(result);
        } else if (result.status === 'PENDING') {
            showPending(result);
        } else if (result.status === 'FAILED') {
            showFailed(result);
        } else {
            showPending({ message: 'Checking payment status...' });
        }
        
    } catch (error) {
        console.error('❌ Status check error:', error);
        showError('Failed to check payment status. Please try again.');
    }
}

// Show success state
function showSuccess(data) {
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('pendingState').style.display = 'none';
    document.getElementById('failedState').style.display = 'none';
    document.getElementById('successState').style.display = 'block';
    
    const details = document.getElementById('successDetails');
    details.innerHTML = `
        <p><strong>Amount:</strong> ₹${data.amount || '0.00'}</p>
        <p><strong>Order ID:</strong> ${orderId}</p>
        ${data.utr ? `<p><strong>UTR:</strong> ${data.utr}</p>` : ''}
        <p><strong>Status:</strong> <span class="success">SUCCESS</span></p>
    `;
    
    console.log('✅ Payment successful!');
}

// Show pending state
function showPending(data) {
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('successState').style.display = 'none';
    document.getElementById('failedState').style.display = 'none';
    document.getElementById('pendingState').style.display = 'block';
    
    const message = document.getElementById('pendingMessage');
    message.innerHTML = data.message || 'Payment is pending. Please wait 10-20 minutes.';
    
    console.log('⏳ Payment pending');
}

// Show failed state
function showFailed(data) {
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('successState').style.display = 'none';
    document.getElementById('pendingState').style.display = 'none';
    document.getElementById('failedState').style.display = 'block';
    
    console.log('❌ Payment failed');
}

// Show error
function showError(message) {
    document.getElementById('statusContainer').innerHTML = `
        <div class="status-icon">⚠️</div>
        <h1 class="status-title failed">Error</h1>
        <p class="status-message">${message}</p>
        <a href="wallet.html" class="btn btn-primary">Go to Wallet</a>
    `;
}

console.log('✅ Payment status script loaded');
