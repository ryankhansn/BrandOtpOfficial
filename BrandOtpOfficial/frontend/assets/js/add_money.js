// frontend/assets/js/add_money.js - FINAL WORKING VERSION

document.addEventListener('DOMContentLoaded', () => {
    const addMoneyForm = document.getElementById('addMoneyForm');
    if (!addMoneyForm) return;

    const amountInput = document.getElementById('amount');
    const mobileInput = document.getElementById('mobile');
    const messageDiv = document.getElementById('message');
    const submitButton = document.getElementById('addMoneyBtn');

    // ✅ FIX 1: API का पूरा और सही URL यहाँ डालें
    const API_BASE_URL = 'https://brandotpofficial.onrender.com';

    function showMessage(text, type = 'error') {
        if (messageDiv) {
            messageDiv.textContent = text;
            messageDiv.className = `message ${type}`;
            messageDiv.style.display = 'block';
        }
    }

    addMoneyForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        submitButton.disabled = true;
        submitButton.textContent = 'Processing...';
        if (messageDiv) messageDiv.style.display = 'none';

        const token = localStorage.getItem('token');
        if (!token) {
            showMessage('You are not authenticated. Please log in again.');
            submitButton.disabled = false;
            submitButton.textContent = 'Proceed to Pay0';
            return;
        }

        const amount = parseFloat(amountInput.value);
        const mobile = mobileInput.value;

        if (isNaN(amount) || amount < 50 || amount > 5000) {
            showMessage('Please enter an amount between ₹50 and ₹5,000.');
            submitButton.disabled = false;
            submitButton.textContent = 'Proceed to Pay0';
            return;
        }

        if (!/^\d{10}$/.test(mobile)) {
            showMessage('Please enter a valid 10-digit mobile number.');
            submitButton.disabled = false;
            submitButton.textContent = 'Proceed to Pay0';
            return;
        }

        try {
            // ✅ FIX 2: पूरे URL का उपयोग करें
            const response = await fetch(`${API_BASE_URL}/api/payments/pay0/create-order`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    amount: amount,
                    customer_mobile: mobile
                })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'Failed to create order.');
            }

            if (result.payment_url || result.paymenturl) {
                // ✅ दोनों कीज़ (payment_url और paymenturl) को हैंडल करें
                window.location.href = result.payment_url || result.paymenturl;
            } else {
                throw new Error('Payment URL not received from server.');
            }

        } catch (error) {
            showMessage(error.message);
            submitButton.disabled = false;
            submitButton.textContent = 'Proceed to Pay0';
        }
    });
});
