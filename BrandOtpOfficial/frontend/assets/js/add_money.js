const API_BASE_URL = window.API_BASE_URL || 'https://brandotpofficial.onrender.com';

const form = document.getElementById("addMoneyForm");
const amount = document.getElementById("amount");
const mobile = document.getElementById("mobile_number");
const msgBox = document.getElementById("message");
const btn = document.getElementById("addMoneyBtn");

function setAmount(v) {
  amount.value = v;
  amount.focus();
}

function showMessage(text, type) {
  msgBox.textContent = text;
  msgBox.className = `message ${type}`;
  msgBox.style.display = "block";
}

function clearMessage() {
  msgBox.style.display = "none";
}

form.addEventListener("submit", async e => {
  e.preventDefault();
  clearMessage();
  btn.disabled = true;

  try {
    const amt = parseFloat(amount.value);
    if (isNaN(amt) || amt < 50 || amt > 5000) throw new Error("Enter amount ₹50–₹5 000");
    if (!/^\d{10}$/.test(mobile.value)) throw new Error("Enter valid 10-digit mobile");

    const res = await fetch(`${API_BASE_URL}/api/payments/pay0/create-order`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mobile: mobile.value, amount: amt })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Gateway error");
    }

    const response = await res.json();
    if (!response.payment_url || typeof response.payment_url !== "string") {
      throw new Error("Server did not return a payment link!");
    }
    window.location.href = response.payment_url;

  } catch (err) {
    showMessage(err.message || "Payment error", "error");
  } finally {
    btn.disabled = false;
  }
});
