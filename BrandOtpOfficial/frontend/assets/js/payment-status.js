document.addEventListener('DOMContentLoaded', () => {
    const statusMessage = document.getElementById('status-message');
    const loader = document.querySelector('.loader');
    const dashboardLink = document.getElementById('dashboard-link');

    const checkPaymentStatus = async () => {
        const urlParams = new URLSearchParams(window.location.search);
        const orderId = urlParams.get('orderid');

        if (!orderId) {
            statusMessage.textContent = 'Error: Order ID not found in URL.';
            loader.style.display = 'none';
            return;
        }

        try {
            const token = localStorage.getItem('token');
            if (!token) {
                statusMessage.textContent = 'Authentication error. Please log in again.';
                loader.style.display = 'none';
                return;
            }

            // Replace with your actual backend URL
            const backendUrl = 'https://brandotpofficial.onrender.com';
            
            const response = await fetch(`${backendUrl}/api/payments/check-status/${orderId}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            const result = await response.json();

            loader.style.display = 'none';

            if (response.ok && result.success) {
                statusMessage.textContent = result.message || 'Payment successful and balance updated!';
                statusMessage.style.color = 'green';
                dashboardLink.style.display = 'block';
            } else {
                statusMessage.textContent = result.detail || 'Payment verification failed. Please contact support.';
                statusMessage.style.color = 'red';
            }

        } catch (error) {
            loader.style.display = 'none';
            statusMessage.textContent = 'An error occurred while checking status. Please check your dashboard or contact support.';
            statusMessage.style.color = 'red';
            console.error('Error checking payment status:', error);
        }
    };

    checkPaymentStatus();
});
