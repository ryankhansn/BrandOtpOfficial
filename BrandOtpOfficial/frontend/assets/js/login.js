// frontend/assets/js/login.js - FINAL WORKING VERSION

const API_BASE_URL = window.API_BASE_URL || 'https://brandotpofficial.onrender.com';

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const messageDiv = document.getElementById('messageContainer');
        const submitBtn = document.getElementById('submitBtn');
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        submitBtn.disabled = true;
        submitBtn.textContent = 'Logging in...';
        if (messageDiv) messageDiv.style.display = 'none';

        try {
            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);

            const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'Login failed. Please check credentials.');
            }

            if (result.access_token) {
                // --- ✅ यही है सबसे महत्वपूर्ण लाइन ---
                // हम टोकन को हमेशा 'token' नाम से सेव करेंगे
                localStorage.setItem('token', result.access_token);
                // ---------------------------------
                
                if (result.user) {
                    localStorage.setItem('user', JSON.stringify(result.user));
                }

                messageDiv.className = 'message success-message';
                messageDiv.textContent = '🎉 Login successful! Redirecting...';
                messageDiv.style.display = 'block';

                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1000);

            } else {
                throw new Error('Token not found in server response.');
            }

        } catch (error) {
            if (messageDiv) {
                messageDiv.className = 'message error-message';
                messageDiv.textContent = '❌ ' + error.message;
                messageDiv.style.display = 'block';
            }
            submitBtn.disabled = false;
            submitBtn.textContent = 'Login';
        }
    });
});
