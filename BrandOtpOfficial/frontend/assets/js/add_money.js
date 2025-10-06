// frontend/assets/js/add_money.js - DEBUGGING VERSION

document.addEventListener('DOMContentLoaded', () => {
    const messageDiv = document.getElementById('message');
    const form = document.querySelector('form');
    const button = form.querySelector('button');

    // फॉर्म को डिसेबल कर दें ताकि कोई पेमेंट न हो
    form.addEventListener('submit', e => e.preventDefault());
    button.disabled = true;
    button.textContent = "Debugging in Progress";

    // --- ✅ डीबगिंग शुरू ---
    // यह कोड पेज लोड होते ही चलेगा और हमें बताएगा कि localStorage में क्या है
    
    if (messageDiv) {
        messageDiv.style.display = 'block';
        messageDiv.style.textAlign = 'left';
        messageDiv.style.fontFamily = 'monospace';
        messageDiv.style.whiteSpace = 'pre-wrap';
        messageDiv.style.backgroundColor = '#f0f0f0';
        messageDiv.style.color = '#000';
        messageDiv.style.border = '2px solid #ccc';
        messageDiv.style.padding = '15px';

        let debugInfo = '--- STORAGE DEBUG ON ADD_MONEY PAGE ---\n\n';
        
        // 'token' को पढ़ने की कोशिश करें
        const token = localStorage.getItem('token');
        debugInfo += `1. Reading 'token' from localStorage...\n   Result: ${token}\n\n`;

        if (token) {
            debugInfo += 'STATUS: Token Found! The error should be gone.\n\n';
        } else {
            debugInfo += 'STATUS: Token NOT Found! This is why you see "Not Authenticated".\n\n';
        }

        // देखें कि कहीं यह 'access_token' नाम से तो सेव नहीं है
        const accessToken = localStorage.getItem('access_token');
        debugInfo += `2. Reading 'access_token' from localStorage...\n   Result: ${accessToken}\n\n`;

        // localStorage में मौजूद सभी आइटम्स को लिस्ट करें
        debugInfo += '--- ALL ITEMS IN LOCAL STORAGE ---\n';
        if (localStorage.length > 0) {
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                const value = localStorage.getItem(key);
                debugInfo += `- Key: "${key}", Value: "${value.substring(0, 30)}..."\n`;
            }
        } else {
            debugInfo += '(localStorage is completely empty)';
        }
        
        messageDiv.textContent = debugInfo;
    }
    // --- डीबगिंग खत्म ---
});
