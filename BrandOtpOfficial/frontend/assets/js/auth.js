// frontend/assets/js/auth.js - The Only Auth File You Need

const API_BASE_URL = window.API_BASE_URL || 'https://brandotpofficial.onrender.com';

document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("login-form");
    const signupForm = document.getElementById("signup-form");
    const messageContainer = document.getElementById("messageContainer");

    // Tab switching logic
    document.querySelectorAll(".auth-tab").forEach(tab => {
        tab.addEventListener("click", () => {
            document.querySelectorAll(".auth-tab").forEach(t => t.classList.remove("active"));
            tab.classList.add("active");
            document.querySelectorAll(".auth-form").forEach(form => form.classList.remove("active"));
            document.getElementById(`${tab.dataset.tab}-form`).classList.add("active");
            if (messageContainer) messageContainer.style.display = 'none';
        });
    });

    // Automatically switch to signup tab if URL has #signup
    if (window.location.hash === '#signup') {
        document.querySelector('.auth-tab[data-tab="signup"]').click();
    }

    // Helper function to show messages
    function showMessage(message, type) {
        if (!messageContainer) return;
        messageContainer.textContent = message;
        messageContainer.className = `message ${type}-message`;
        messageContainer.style.display = 'block';
    }

    // ===== LOGIN LOGIC =====
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("login-email").value.trim();
            const password = document.getElementById("login-password").value.trim();
            const button = loginForm.querySelector('button');
            button.disabled = true;

            try {
                const formData = new URLSearchParams();
                formData.append('username', email);
                formData.append('password', password);

                const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/x-form-urlencoded" },
                    body: formData
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

    // ===== SIGNUP LOGIC =====
    if (signupForm) {
        signupForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const username = document.getElementById("signup-username").value.trim();
            const email = document.getElementById("signup-email").value.trim();
            const password = document.getElementById("signup-password").value.trim();
            const button = signupForm.querySelector('button');
            button.disabled = true;

            if (password.length < 6) {
                showMessage('Password must be at least 6 characters.', 'error');
                button.disabled = false;
                return;
            }

            try {
                const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, email, password })
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || "Signup failed");

                showMessage("✅ Signup successful! Please switch to the login tab.", 'success');
            } catch (err) {
                showMessage(`⚠️ ${err.message}`, 'error');
            } finally {
                button.disabled = false;
            }
        });
    }
});
