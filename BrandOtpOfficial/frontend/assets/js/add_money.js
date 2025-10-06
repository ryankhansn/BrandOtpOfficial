// frontend/assets/js/add_money.js

const API_BASE_URL = window.API_BASE_URL || 'https://brandotpofficial.onrender.com';

const form = document.getElementById("addMoneyForm");
const amountInput = document.getElementById("amount");
// मोबाइल नंबर की अब हमें फ्रंटएंड से ज़रूरत नहीं है, क्योंकि हम इसे लॉग-इन यूजर से लेंगे।
// const mobileInput = document.getElementById("mobile_number"); 
const msgBox = document.getElementById("message");
const btn = document.getElementById("addMoneyBtn");

function setAmount(v) {
  amountInput.value = v;
  amountInput.focus();
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
  btn.textContent = "Processing..."; // बटन का टेक्स्ट बदलें

  try {
    // --- ✅ मुख्य बदलाव: लोकल स्टोरेज से टोकन प्राप्त करें ---
    const token = localStorage.getItem('token');
    if (!token) {
      // अगर यूजर लॉग-इन नहीं है, तो उसे बताएं
      throw new Error("You are not authenticated. Please log in again.");
    }
    // ------------------------------------------------------

    const amt = parseFloat(amountInput.value);
    if (isNaN(amt) || amt < 50 || amt > 5000) {
      throw new Error("Please enter an amount between ₹50 and ₹5,000.");
    }
    
    // अब हमें फ्रंटएंड से मोबाइल नंबर भेजने की ज़रूरत नहीं है।

    const res = await fetch(`${API_BASE_URL}/api/payments/pay0/create-order`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        // --- ✅ मुख्य बदलाव: Authorization हेडर भेजें ---
        "Authorization": `Bearer ${token}`
      },
      // बॉडी में अब सिर्फ amount भेजें
      body: JSON.stringify({ amount: amt })
    });

    const result = await res.json();
    
    if (!res.ok) {
      throw new Error(result.detail || "Failed to create payment order.");
    }

    if (!result.payment_url || typeof result.payment_url !== "string") {
      throw new Error("Server did not return a valid payment link!");
    }
    
    // यूजर को Pay0 के पेमेंट पेज पर भेजें
    window.location.href = result.payment_url;

  } catch (err) {
    showMessage(err.message || "An error occurred during payment.", "error");
    btn.disabled = false; // एरर आने पर बटन को फिर से इनेबल करें
    btn.textContent = "Proceed to Pay0"; // बटन का टेक्स्ट वापस सेट करें
  }
  // `finally` ब्लॉक को यहाँ से हटा दिया गया है ताकि सफल होने पर बटन डिसेबल रहे
});
