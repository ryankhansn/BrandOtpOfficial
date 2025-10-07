// frontend/assets/js/dashboard.js - TOKEN HELPER ONLY

const API_BASE_URL = 'https://brandotpofficial.onrender.com';

// Export token for other pages
window.getToken = function() {
    return localStorage.getItem('token');
};

// Export user info
window.getUserInfo = function() {
    return {
        token: localStorage.getItem('token'),
        username: localStorage.getItem('username'),
        email: localStorage.getItem('email'),
        userId: localStorage.getItem('userId')
    };
};

// Export API base URL
window.getAPIBaseURL = function() {
    return API_BASE_URL;
};

// Quick logout
window.logout = function() {
    localStorage.clear();
    window.location.replace('/auth');
};

console.log('✅ Token helper loaded - API:', API_BASE_URL);
