document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = 'https://brandotpofficial.onrender.com';
    const statusMessage = document.getElementById('status-message');
    const loader = document.querySelector('.loader');
    const dashboardLink = document.getElementById('dashboard-link');

    const verifyPayment = async () => {
        const urlParams = new URLSearchParams(window.location.search);
        // ✅ FIX: Pay0 से 'orderid' आता है, 'order_id' नहीं
        const orderId = urlParams.get('orderid'); 
        const token = localStorage.getItem('token');

        if (!orderId) {
            statusMessage.textContent = 'Error: Order ID not found in URL.';
            loader.style.display = 'none';
            return;
        }
        if (!token) {
            statusMessage.textContent = 'Authentication Error. Please log in to see the status.';
            loader.style.display = 'none';
            return;
        }

        try {
            statusMessage.textContent = 'Verifying your payment, please wait...';
            
            // ✅ FIX: API का URL और मेथड सही किया गया है
            const res = await fetch(`${API_BASE_URL}/api/payments/verify-payment/${orderId}`, {
                method: 'GET', // ✅ मेथड GET होना चाहिए जैसा हमने बैकएंड में बनाया है
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.detail || 'Payment verification failed.');
            }

            // ✅ पेमेंट सफल!
            statusMessage.textContent = '✅ Payment Successful! Your wallet has been updated.';
            statusMessage.style.color = 'green';
            dashboardLink.style.display = 'block';

        } catch (error) {
            statusMessage.textContent = `❌ Verification Failed: ${error.message}`;
            statusMessage.style.color = 'red';
            dashboardLink.style.display = 'block';
        } finally {
            loader.style.display = 'none';
        }
    };

    verifyPayment();
});
