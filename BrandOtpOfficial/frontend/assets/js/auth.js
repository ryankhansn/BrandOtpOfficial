// frontend/assets/js/auth.js - FINAL WORKING VERSION

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

    if (window.location.hash === '#signup') {
        document.querySelector('.auth-tab[data-tab="signup"]').click();
    }

    function showMessage(message, type) {
        if (!messageContainer) return;
        messageContainer.textContent = message;
        messageContainer.className = `message ${type}-message`;
        messageContainer.style.display = 'block';
    }

    // ===== ✅ LOGIN - FIXED FOR YOUR BACKEND! =====
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

                // ✅ FIX: Your backend /auth/login expects JSON (UserLogin model)
                const res = await fetch(`${API_BASE_URL}/auth/login`, {
                    method: "POST",
                    headers: { 
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    body: JSON.stringify({ 
                        email: email, 
                        password: password 
                    })
                });

                const data = await res.json();
                console.log('📦 Login response:', data);
                
                if (!res.ok) {
                    throw new Error(data.detail || "Login failed");
                }
                
                // ✅ Token save - Your backend returns 'access_token'
                localStorage.setItem("token", data.access_token);
                localStorage.setItem("username", data.user.username);
                localStorage.setItem("email", data.user.email);
                localStorage.setItem("userId", data.user.id);
                
                console.log('✅ Token saved:', data.access_token.substring(0, 20) + '...');
                
                showMessage("✅ Login successful! Redirecting to dashboard...", 'success');
                
                // ✅ Redirect to dashboard
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

    // ===== ✅ SIGNUP - ALREADY CORRECT! =====
    if (signupForm) {
        signupForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const username = document.getElementById("signup-username").value.trim();
            const email = document.getElementById("signup-email").value.trim();
            const password = document.getElementById("signup-password").value.trim();
            const button = signupForm.querySelector('button');
            button.disabled = true;
            button.textContent = 'Creating account...';

            if (password.length < 4) {
                showMessage('⚠️ Password must be at least 4 characters.', 'error');
                button.disabled = false;
                button.textContent = 'Create Account';
                return;
            }

            try {
                console.log('📝 Signup attempt:', email);

                // ✅ Signup expects JSON (UserSignup model)
                const res = await fetch(`${API_BASE_URL}/auth/signup`, {
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

                // ✅ Auto-login after signup with token
                localStorage.setItem("token", data.access_token);
                localStorage.setItem("username", data.user.username);
                localStorage.setItem("email", data.user.email);
                localStorage.setItem("userId", data.user.id);

                showMessage("✅ Account created! Redirecting to dashboard...", 'success');
                
                // ✅ Redirect to dashboard after signup
                setTimeout(() => {
                    window.location.href = "/dashboard";
                }, 1500);
                
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

// ✅ Auto-redirect if already logged in
if (window.location.pathname.includes('auth.html') && isLoggedIn()) {
    console.log('✅ Already logged in, redirecting to dashboard');
    window.location.href = '/dashboard';
}
