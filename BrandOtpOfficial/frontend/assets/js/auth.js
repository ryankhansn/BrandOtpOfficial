// frontend/assets/js/auth.js - The Only Auth File You Need

const API_BASE_URL = window.API_BASE_URL || 'https://brandotpofficial.onrender.com';
console.log('🔐 Auth System Initialized. API:', API_BASE_URL);

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
            messageContainer.style.display = 'none'; // Hide messages on tab switch
        });
    });

    // Helper function to show messages
    function showMessage(message, type) {
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

            try {
                const formData = new URLSearchParams();
                formData.append('username', email); // FastAPI OAuth2 expects 'username'
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
                setTimeout(() => window.location.href = "dashboard.html", 1500);
            } catch (err) {
                showMessage(`⚠️ ${err.message}`, 'error');
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
            if (password.length < 6) {
                showMessage('Password must be at least 6 characters.', 'error');
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
            }
        });
    }
});
