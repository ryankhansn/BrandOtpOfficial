// frontend/assets/js/login.js - DEBUGGING VERSION

const API_BASE_URL = window.API_BASE_URL || 'https://brandotpofficial.onrender.com';
console.log('🔐 Login API is set to:', API_BASE_URL);

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
                throw new Error(result.detail || 'Login failed.');
            }

            if (result.access_token) {
                // --- ✅ डीबगिंग शुरू ---
                console.log('--- LOGIN DEBUGGING ---');
                console.log('Server sent this access_token:', result.access_token);
                
                // टोकन को 'token' नाम से localStorage में सेव करें
                localStorage.setItem('token', result.access_token);
                
                // तुरंत वापस पढ़ें और देखें कि क्या यह सेव हुआ
                const savedToken = localStorage.getItem('token');
                console.log('Value read back from localStorage:', savedToken);
                
                if (savedToken) {
                    console.log('✅ SUCCESS: Token was set in localStorage.');
                } else {
                    console.error('❌ CRITICAL ERROR: FAILED to set token in localStorage!');
                }
                console.log('--------------------');
                // --- डीबगिंग खत्म ---
                
                messageDiv.className = 'message success-message';
                messageDiv.textContent = '🎉 Login successful! Redirecting...';
                messageDiv.style.display = 'block';

                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1500);

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
