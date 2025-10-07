// frontend/assets/js/api.js - COMPLETE FIXED VERSION

const API_BASE_URL = 'https://brandotpofficial.onrender.com';

async function apiRequest(endpoint, method = 'GET', data = null, token = null) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = { 'Content-Type': 'application/json' };
    
    if (token) headers['Authorization'] = `Bearer ${token}`;
    
    const options = { method, headers };
    if (data && method !== 'GET') options.body = JSON.stringify(data);
    
    const response = await fetch(url, options);
    const result = await response.json();
    
    if (!response.ok) {
        throw new Error(result.detail || 'API request failed');
    }
    
    return result;
}

// ✅ MAIN API FUNCTIONS - ALL FIXED WITH /api PREFIX!
const api = {
    // ✅ FIXED Authentication - Added /api prefix
    auth: {
        login: async (email, password) => {
            // ✅ FIX: Backend expects JSON at /api/auth/login
            const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || 'Login failed');
            
            // Save token and redirect
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('username', email);
            
            return data;
        },
        
        signup: async (username, email, password) => {
            // ✅ FIX: Backend expects JSON at /api/auth/signup
            const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || 'Signup failed');
            
            return data;
        },
        
        getProfile: async () => {
            const token = localStorage.getItem('token');
            // ✅ FIX: Added /api prefix
            return apiRequest('/api/auth/me', 'GET', null, token);
        },
        
        logout: () => {
            localStorage.removeItem('token');
            localStorage.removeItem('username');
            window.location.href = '/auth.html';
        }
    },
    
    // ✅ Wallet Operations - Added /api prefix
    wallet: {
        getBalance: async () => {
            const token = localStorage.getItem('token');
            // ✅ FIX: Added /api prefix
            return apiRequest('/api/wallet/balance', 'GET', null, token);
        },
        
        addMoney: async (amount) => {
            const token = localStorage.getItem('token');
            const formData = new FormData();
            formData.append('amount', amount);
            formData.append('payment_method', 'manual');
            
            // ✅ FIX: Added /api prefix
            const response = await fetch(`${API_BASE_URL}/api/wallet/add-money`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData
            });
            
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || 'Failed to add money');
            return data;
        },
        
        getTransactions: async () => {
            const token = localStorage.getItem('token');
            // ✅ FIX: Added /api prefix
            return apiRequest('/api/wallet/transactions', 'GET', null, token);
        }
    },
    
    // ✅ SMSMan Services - Added /api prefix
    smsman: {
        getServices: async () => {
            // ✅ FIX: Added /api prefix
            const data = await apiRequest('/api/smsman/services');
            console.log('✅ Services loaded:', data.services);
            return data.services || [];
        },
        
        getMeta: async () => {
            // ✅ FIX: Added /api prefix
            return apiRequest('/api/smsman/meta');
        },
        
        getPrice: async (applicationId, countryId) => {
            // ✅ FIX: Added /api prefix
            return apiRequest(`/api/smsman/price/${applicationId}/${countryId}`);
        },
        
        buyNumber: async (applicationId, countryId) => {
            const token = localStorage.getItem('token');
            // ✅ FIX: Added /api prefix
            return apiRequest('/api/smsman/buy', 'POST', {
                application_id: applicationId,
                country_id: countryId
            }, token);
        },
        
        getSMS: async (requestId) => {
            const token = localStorage.getItem('token');
            // ✅ FIX: Added /api prefix
            return apiRequest(`/api/smsman/sms/${requestId}`, 'GET', null, token);
        },
        
        cancel: async (requestId) => {
            const token = localStorage.getItem('token');
            // ✅ FIX: Added /api prefix
            return apiRequest(`/api/smsman/cancel/${requestId}`, 'POST', null, token);
        }
    },
    
    // ✅ Pricing Helpers (NO CHANGES)
    pricing: {
        formatPrice: (price) => `₹${Number(price).toFixed(2)}`,
        
        canAfford: (userBalance, servicePrice) => 
            Number(userBalance) >= Number(servicePrice),
            
        getShortage: (userBalance, servicePrice) => {
            const shortage = Number(servicePrice) - Number(userBalance);
            return shortage > 0 ? shortage : 0;
        }
    },
    
    // ✅ Complete Purchase Flow (NO CHANGES - uses api.smsman internally)
    purchase: {
        buyService: async (serviceId, countryId = 91) => {
            try {
                console.log(`🛒 Buying service: ${serviceId}`);
                
                const balance = await api.wallet.getBalance();
                console.log(`💰 Balance: ₹${balance.balance}`);
                
                const priceInfo = await api.smsman.getPrice(serviceId, countryId);
                console.log(`💰 Price: ${api.pricing.formatPrice(priceInfo.user_price)}`);
                
                if (!api.pricing.canAfford(balance.balance, priceInfo.user_price)) {
                    const shortage = api.pricing.getShortage(balance.balance, priceInfo.user_price);
                    throw new Error(`Insufficient balance! Need ${api.pricing.formatPrice(shortage)} more`);
                }
                
                const result = await api.smsman.buyNumber(serviceId, countryId);
                console.log('✅ Purchase successful:', result);
                
                return { success: true, ...result, pricing: priceInfo };
                
            } catch (error) {
                console.error('❌ Purchase failed:', error);
                throw error;
            }
        }
    }
};

// ✅ UI HELPERS (NO CHANGES)
async function loadServicesWithPrices() {
    try {
        const services = await api.smsman.getServices();
        const balance = await api.wallet.getBalance();
        
        console.log('✅ Services:', services);
        console.log('✅ Balance:', balance.balance);
        
        services.forEach(service => {
            console.log(`${service.name}: ${service.display_price}`);
        });
        
        return services;
    } catch (error) {
        console.error('❌ Failed to load services:', error);
        return [];
    }
}

async function handleBuyClick(serviceId) {
    try {
        const result = await api.purchase.buyService(serviceId);
        alert(`✅ Success!\nNumber: ${result.number}\nCharged: ${result.transaction.charged_amount}\nNew Balance: ₹${result.transaction.new_balance}`);
        
        location.reload();
    } catch (error) {
        alert(`❌ Purchase failed: ${error.message}`);
    }
}

// Auto-load on page ready
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname.includes('dashboard') || window.location.pathname.includes('services')) {
        loadServicesWithPrices();
    }
});

// Make api available globally
window.api = api;
window.loadServicesWithPrices = loadServicesWithPrices;
window.handleBuyClick = handleBuyClick;
