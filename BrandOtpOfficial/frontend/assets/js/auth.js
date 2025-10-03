// API Configuration - MUST BE AT TOP
const API_BASE_URL = window.API_BASE_URL || 'https://brandotpofficial.onrender.com';
console.log('🔐 Auth - Using API:', API_BASE_URL);

// auth.js
document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("login-form");
  const signupForm = document.getElementById("signup-form");
  const loginError = document.getElementById("login-error");
  const signupError = document.getElementById("signup-error");

  // Tab switch
  document.querySelectorAll(".auth-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".auth-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      document.querySelectorAll(".auth-form").forEach(form => form.classList.remove("active"));
      document.getElementById(`${tab.dataset.tab}-form`).classList.add("active");
    });
  });

  // Login
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const email = document.getElementById("login-email").value.trim();
      const password = document.getElementById("login-password").value.trim();

      try {
        const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (res.ok) {
          localStorage.setItem("token", data.access_token);
          alert("✅ Login successful!");
          window.location.href = "dashboard.html"; // Relative path
        } else {
          loginError.textContent = data.detail || "❌ Login failed";
        }
      } catch (err) {
        loginError.textContent = "⚠️ Server error, try again later.";
        console.error(err);
      }
    });
  }

  // Signup
  if (signupForm) {
    signupForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const username = document.getElementById("signup-username").value.trim();
      const email = document.getElementById("signup-email").value.trim();
      const password = document.getElementById("signup-password").value.trim();
      const confirmPassword = document.getElementById("signup-confirm-password").value.trim();

      if (password !== confirmPassword) {
        signupError.textContent = "❌ Passwords do not match!";
        return;
      }

      try {
        const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, email, password })
        });

        const data = await res.json();

        if (res.ok) {
          alert("✅ Signup successful! Please login.");
          window.location.href = "auth.html"; // Relative path
        } else {
          signupError.textContent = data.detail || "❌ Signup failed";
        }
      } catch (err) {
        signupError.textContent = "⚠️ Server error, try again later.";
        console.error(err);
      }
    });
  }
});
