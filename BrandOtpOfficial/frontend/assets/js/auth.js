// frontend/assets/js/auth.js - FINAL VERSION WITH SIGNUP→LOGIN REDIRECT

const API_BASE_URL = window.API_BASE_URL || 'https://brandotpofficial.onrender.com';
console.log('🔐 Auth System Initialized. API:', API_BASE_URL);

document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("login-form");
    const signupForm = document.getElementById("signup-form");
    const messageContainer = document.getElementById("messageContainer");

    // ✅ Tab switching logic
    document.querySelectorAll(".auth-tab").forEach(tab => {
        tab.addEventListener("click", () => {
            document.querySelectorAll(".auth-tab").forEach(t => t.classList.remove("active"));
            tab.classList.add("active");
            document.querySelectorAll(".auth-form").forEach(form => form.classList.remove("active"));
            document.getElementById(`${tab.dataset.tab}-form`).classList.add("active");
            if (messageContainer) messageContainer.style.display = 'none';
        });
    });

    // ✅ Check URL hash for signup tab
    if (window.location.hash === '#signup') {
        document.querySelector('.auth-tab[data-tab="signup"]').click();
    }

    function showMessage(message, type) {
        if (!messageContainer) return;
        messageContainer.textContent = message;
        messageContainer.className = `message ${type}-message`;
        messageContainer.style.display = 'block';
    }

    // ===== ✅ LOGIN - COMPLETE FIXED! =====
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("login-email").value.trim();
            const password = document.getElementById("login-password").value.trim();
            const button = loginForm.querySelector('button');
            button.disabled = true;
            button.textContent = 'Logging in...';

            try {
                console.log('🔐 Login attempt:', email);

                // ✅ Backend API call with /api prefix
                const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
                    method: "POST",
                    headers: { 
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    body: JSON.stringify({ email, password })
                });

                const data = await res.json();
                console.log('📦 Login response:', data);
                
                if (!res.ok) {
                    throw new Error(data.detail || "Login failed");
                }
                
                // ✅ Save token and user data
                localStorage.setItem("token", data.access_token);
                localStorage.setItem("username", data.user.username);
                localStorage.setItem("email", data.user.email);
                localStorage.setItem("userId", data.user.id);
                
                console.log('✅ Token saved successfully');
                
                showMessage("✅ Login successful! Redirecting to dashboard...", 'success');
                
                // ✅ Redirect to dashboard (clean URL without .html)
                setTimeout(() => {
                    window.location.href = "/dashboard";
                }, 1000);
                
            } catch (err) {
                console.error('❌ Login Error:', err);
                showMessage(`⚠️ ${err.message}`, 'error');
                button.disabled = false;
                button.textContent = 'Login';
            }
        });
    }

    // ===== ✅ SIGNUP - FIXED WITH LOGIN REDIRECT! =====
    if (signupForm) {
        signupForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const username = document.getElementById("signup-username").value.trim();
            const email = document.getElementById("signup-email").value.trim();
            const password = document.getElementById("signup-password").value.trim();
            const button = signupForm.querySelector('button');
            button.disabled = true;
            button.textContent = 'Creating account...';

            // ✅ Password validation
            if (password.length < 4) {
                showMessage('⚠️ Password must be at least 4 characters.', 'error');
                button.disabled = false;
                button.textContent = 'Create Account';
                return;
            }

            try {
                console.log('📝 Signup attempt:', email);

                // ✅ Backend API call with /api prefix
                const res = await fetch(`${API_BASE_URL}/api/auth/signup`, {
                    method: "POST",
                    headers: { 
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    body: JSON.stringify({ username, email, password })
                });

                const data = await res.json();
                console.log('📦 Signup response:', data);
                
                if (!res.ok) {
                    throw new Error(data.detail || "Signup failed");
                }

                // ✅ SUCCESS: Show message and switch to login tab
                showMessage("✅ Account created successfully! Please login to continue.", 'success');
                
                // ✅ Pre-fill login email field
                document.getElementById("login-email").value = email;
                
                // ✅ Switch to login tab after 2 seconds
                setTimeout(() => {
                    document.querySelector('.auth-tab[data-tab="login"]').click();
                    if (messageContainer) messageContainer.style.display = 'none';
                }, 2000);
                
            } catch (err) {
                console.error('❌ Signup Error:', err);
                showMessage(`⚠️ ${err.message}`, 'error');
            } finally {
                button.disabled = false;
                button.textContent = 'Create Account';
            }
        });
    }
});

// ✅ Check if user is already logged in
function isLoggedIn() {
    return localStorage.getItem('token') !== null;
}

// ✅ Auto-redirect if already logged in (when visiting auth page)
if ((window.location.pathname.includes('auth') || window.location.pathname.includes('login')) && isLoggedIn()) {
    console.log('✅ Already logged in, redirecting to dashboard');
    window.location.href = '/dashboard';
}
