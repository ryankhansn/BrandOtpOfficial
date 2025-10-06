document.addEventListener('DOMContentLoaded', () => {
    // फॉर्म और अन्य एलिमेंट्स को चुनें
    const addMoneyForm = document.querySelector('form'); // फॉर्म को चुनें, उसे कोई ID देने की ज़रूरत नहीं
    const amountInput = document.getElementById('amount');
    const messageDiv = document.getElementById('message');
    const submitButton = addMoneyForm.querySelector('button[type="submit"]');

    // संदेश दिखाने के लिए एक फंक्शन
    function showMessage(text, type = 'error') {
        if (messageDiv) {
            messageDiv.textContent = text;
            messageDiv.className = `message ${type}`;
            messageDiv.style.display = 'block';
        }
    }

    // फॉर्म सबमिट होने पर यह फंक्शन चलेगा
    addMoneyForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // पेज को रीलोड होने से रोकें

        // बटन को डिसेबल करें और टेक्स्ट बदलें
        submitButton.disabled = true;
        submitButton.textContent = 'Processing...';
        if(messageDiv) messageDiv.style.display = 'none';

        // 1. localStorage से टोकन प्राप्त करें
        const token = localStorage.getItem('token');

        // 2. अगर टोकन नहीं है, तो एरर दिखाएँ
        if (!token) {
            showMessage('You are not authenticated. Please log in again.');
            submitButton.disabled = false;
            submitButton.textContent = 'Proceed to Pay0';
            return;
        }

        const amount = parseFloat(amountInput.value);

        // 3. रकम की जाँच करें
        if (isNaN(amount) || amount < 50 || amount > 5000) {
            showMessage('Please enter an amount between ₹50 and ₹5,000.');
            submitButton.disabled = false;
            submitButton.textContent = 'Proceed to Pay0';
            return;
        }

        try {
            // 4. बैकएंड को टोकन के साथ रिक्वेस्ट भेजें
            const response = await fetch('https://brandotpofficial.onrender.com/api/payments/pay0/create-order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}` // यह सबसे महत्वपूर्ण लाइन है
                },
                body: JSON.stringify({ amount: amount })
            });

            const result = await response.json();

            // 5. अगर रिक्वेस्ट सफल नहीं हुई, तो एरर दिखाएँ
            if (!response.ok) {
                throw new Error(result.detail || 'Failed to create order.');
            }

            // 6. अगर पेमेंट URL मिला है, तो उस पर भेज दें
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
