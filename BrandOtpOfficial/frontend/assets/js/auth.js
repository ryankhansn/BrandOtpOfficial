// frontend/assets/js/auth.js - COMPLETE FIXED VERSION

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

    // If URL has #signup, switch to signup tab
    if (window.location.hash === '#signup') {
        document.querySelector('.auth-tab[data-tab="signup"]').click();
    }

    function showMessage(message, type) {
        if (!messageContainer) return;
        messageContainer.textContent = message;
        messageContainer.className = `message ${type}-message`;
        messageContainer.style.display = 'block';
    }

    // ===== ✅ LOGIN LOGIC - FULLY FIXED! =====
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("login-email").value.trim();
            const password = document.getElementById("login-password").value.trim();
            const button = loginForm.querySelector('button');
            button.disabled = true;
            button.textContent = 'Logging in...';

            try {
                // ✅ FIX 1: FastAPI /auth/login expects FORM DATA (application/x-www-form-urlencoded)
                const formData = new URLSearchParams();
                formData.append('username', email);  // OAuth2 standard uses 'username' field
                formData.append('password', password);
                
                const res = await fetch(`${API_BASE_URL}/auth/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: formData
                });

                const data = await res.json();
                
                if (!res.ok) {
                    throw new Error(data.detail || "Login failed");
                }
                
                // ✅ FIX 2: Save token properly
                localStorage.setItem("token", data.access_token);
                localStorage.setItem("username", email);
                
                showMessage("✅ Login successful! Redirecting to dashboard...", 'success');
                
                // ✅ FIX 3: Redirect after 1 second to dashboard
                setTimeout(() => {
                    window.location.href = "/dashboard.html";
                }, 1000);
                
            } catch (err) {
                console.error('❌ Login Error:', err);
                showMessage(`⚠️ ${err.message}`, 'error');
                button.disabled = false;
                button.textContent = 'Login';
            }
        });
    }

    // ===== ✅ SIGNUP LOGIC - FULLY FIXED! =====
    if (signupForm) {
        signupForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const username = document.getElementById("signup-username").value.trim();
            const email = document.getElementById("signup-email").value.trim();
            const password = document.getElementById("signup-password").value.trim();
            const button = signupForm.querySelector('button');
            button.disabled = true;
            button.textContent = 'Creating account...';

            // Basic validation
            if (password.length < 6) {
                showMessage('⚠️ Password must be at least 6 characters.', 'error');
                button.disabled = false;
                button.textContent = 'Create Account';
                return;
            }

            try {
                // ✅ Signup endpoint expects JSON
                const res = await fetch(`${API_BASE_URL}/auth/signup`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, email, password })
                });

                const data = await res.json();
                
                if (!res.ok) {
                    throw new Error(data.detail || "Signup failed");
                }

                // ✅ FIX 4: After signup, switch to login tab and show success message
                showMessage("✅ Account created successfully! Please login now.", 'success');
                
                // Switch to login tab after 1.5 seconds
                setTimeout(() => {
                    document.querySelector('.auth-tab[data-tab="login"]').click();
                    document.getElementById("login-email").value = email;
                    messageContainer.style.display = 'none';
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
