// frontend/assets/js/login.js

// API Configuration
const API_BASE_URL = window.API_BASE_URL || 'https://brandotpofficial.onrender.com';
console.log('🔐 Login API:', API_BASE_URL);

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔐 Login page loaded');
    
    // Get form elements
    const form = document.getElementById('loginForm');
    const submitBtn = document.getElementById('submitBtn');
    const messageContainer = document.getElementById('messageContainer');
    const welcomeMessage = document.getElementById('welcomeMessage');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    
    if (!form || !submitBtn || !messageContainer) {
        console.error('❌ Required elements not found');
        return;
    }
    
    console.log('✅ All login elements found');

    checkRegistrationStatus();

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        console.log('🔐 Login form submitted');
        
        clearMessage();
        
        const email = emailInput.value.trim();
        const password = passwordInput.value;
        
        const validation = validateLoginForm({ email, password });
        if (!validation.isValid) {
            showMessage(validation.message, 'error');
            return;
        }
        
        setLoadingState(true);
        
        try {
            const formData = new URLSearchParams();
            formData.append('username', email); // FastAPI OAuth2 'username' फील्ड की उम्मीद करता है
            formData.append('password', password);
            
            console.log('📤 Sending login request to API...');
            
            const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData.toString()
            });
            
            console.log('📥 Login response status:', response.status);
            
            const result = await response.json();
            console.log('📋 Login response data:', result);
            
            if (response.ok && result.access_token) {
                showMessage('🎉 Login successful! Redirecting to dashboard...', 'success');
                
                // --- ✅ मुख्य बदलाव: टोकन को 'token' नाम से सेव करें ---
                localStorage.setItem('token', result.access_token);
                // ---------------------------------------------------

                // यूजर की जानकारी को भी सेव कर सकते हैं, यह वैकल्पिक है
                if (result.user) {
                    localStorage.setItem('user', JSON.stringify(result.user));
                }
                
                console.log('✅ Token saved correctly with the name "token".');
                
                sessionStorage.removeItem('registered_email');
                sessionStorage.removeItem('registered_username');
                
                console.log('🚀 Redirecting to dashboard...');
                
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1500);
                
            } else {
                const errorMsg = result.detail || 'Login failed. Please check your credentials.';
                showMessage('❌ ' + errorMsg, 'error');
            }
            
        } catch (error) {
            console.error('❌ Login error:', error);
            showMessage('❌ Network error. Please check your connection.', 'error');
        } finally {
            setLoadingState(false);
        }
    });

    // ===== HELPER FUNCTIONS =====

    function checkRegistrationStatus() {
        const registeredEmail = sessionStorage.getItem('registered_email');
        const registeredUsername = sessionStorage.getItem('registered_username');
        if (registeredEmail && registeredUsername) {
            emailInput.value = registeredEmail;
            document.getElementById('welcomeText').textContent = `Welcome ${registeredUsername}! Please login with your new account.`;
            welcomeMessage.style.display = 'block';
            passwordInput.focus();
        }
    }

    function validateLoginForm(data) {
        if (!data.email || !data.password) return { isValid: false, message: 'Please fill in all fields.' };
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(data.email)) return { isValid: false, message: 'Please enter a valid email.' };
        if (data.password.length < 6) return { isValid: false, message: 'Password must be at least 6 characters.' };
        return { isValid: true };
    }

    function showMessage(message, type) {
        messageContainer.textContent = message;
        messageContainer.className = 'message ' + type + '-message';
        messageContainer.style.display = 'block';
        messageContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function clearMessage() {
        messageContainer.innerHTML = '';
        messageContainer.style.display = 'none';
    }

    function setLoadingState(isLoading) {
        submitBtn.disabled = isLoading;
        submitBtn.textContent = isLoading ? 'Logging in...' : 'Login';
    }
});
