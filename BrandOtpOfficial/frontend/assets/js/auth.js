// frontend/assets/js/auth.js - FINAL & CORRECTED VERSION

const API_BASE_URL = window.API_BASE_URL || 'https://brandotpofficial.onrender.com';
console.log('🔐 Auth System Initialized. API:', API_BASE_URL);

document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("login-form");
    const signupForm = document.getElementById("signup-form");
    const messageContainer = document.getElementById("messageContainer");

    // Tab switching logic (यह सही है, इसे न बदलें)
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

    // ===== LOGIN LOGIC - FIXED! =====
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("login-email").value.trim();
            const password = document.getElementById("login-password").value.trim();
            const button = loginForm.querySelector('button');
            button.disabled = true;

            try {
                // ✅ FIX 1: Sending data as JSON, as required by your API docs
                const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email: email, password: password })
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || "Login failed");
                
                localStorage.setItem("token", data.access_token);
                showMessage("✅ Login successful! Redirecting...", 'success');
                setTimeout(() => window.location.href = "dashboard.html", 1000);
            } catch (err) {
                showMessage(`⚠️ ${err.message}`, 'error');
                button.disabled = false;
            }
        });
    }

    // ===== SIGNUP LOGIC - FIXED! =====
    if (signupForm) {
        signupForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const username = document.getElementById("signup-username").value.trim();
            const email = document.getElementById("signup-email").value.trim();
            const password = document.getElementById("signup-password").value.trim();
            const button = signupForm.querySelector('button');
            button.disabled = true;

            if (password.length < 4) { // आपके डॉक्स के अनुसार min 4 है
                showMessage('Password must be at least 4 characters.', 'error');
                button.disabled = false;
                return;
            }

            try {
                // ✅ FIX 2: Using the correct signup URL from your API docs
                const res = await fetch(`${API_BASE_URL}/api/auth/signup`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, email, password })
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || "Signup failed");

                showMessage("✅ Signup successful! Please login now.", 'success');
            } catch (err) {
                showMessage(`⚠️ ${err.message}`, 'error');
            } finally {
                button.disabled = false;
            }
        });
    }
});
