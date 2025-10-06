// frontend/assets/js/add_money.js - FINAL WORKING VERSION

const API_BASE_URL = window.API_BASE_URL || 'https://brandotpofficial.onrender.com';

document.addEventListener('DOMContentLoaded', () => {
    const addMoneyForm = document.querySelector('form');
    if (!addMoneyForm) return;

    const amountInput = document.getElementById('amount');
    const messageDiv = document.getElementById('message');
    const submitButton = addMoneyForm.querySelector('button[type="submit"]');

    function showMessage(text, type = 'error') {
        if (messageDiv) {
            messageDiv.textContent = text;
            messageDiv.className = `message ${type}-message`;
            messageDiv.style.display = 'block';
        }
    }

    addMoneyForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        submitButton.disabled = true;
        submitButton.textContent = 'Processing...';
        if (messageDiv) messageDiv.style.display = 'none';

        // 1. localStorage से 'token' नाम से टोकन प्राप्त करें
        const token = localStorage.getItem('token');

        if (!token) {
            showMessage('You are not authenticated. Please log in again.');
            submitButton.disabled = false;
            submitButton.textContent = 'Proceed to Pay0';
            return;
        }

        const amount = parseFloat(amountInput.value);

        if (isNaN(amount) || amount < 50 || amount > 5000) {
            showMessage('Please enter an amount between ₹50 and ₹5,000.');
            submitButton.disabled = false;
            submitButton.textContent = 'Proceed to Pay0';
            return;
        }

        try {
            // 2. बैकएंड को टोकन के साथ रिक्वेस्ट भेजें
            const response = await fetch(`${API_BASE_URL}/api/payments/pay0/create-order`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ amount: amount })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'Failed to create order.');
            }

            if (result.payment_url) {
                window.location.href = result.payment_url;
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
