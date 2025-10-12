// frontend/assets/js/buy_number.js - COMPLETE WITH ALL 5 FIXES
console.log('🚀 Buy Number Script Loading...');

// API Configuration
const API_BASE_URL = window.API_BASE_URL || 'https://brandotpofficial.onrender.com';
console.log('🔗 Using API:', API_BASE_URL);

// Global data storage
let countries = [];
let allServices = [];
let filteredServices = [];
let currentPurchase = null;
let smsCheckInterval = null;
let countdownInterval = null;
let secondsLeft = 5;

// DOM elements - Will be initialized after DOM loads
let countrySelect, serviceSelect, countrySearch, serviceSearch;
let serviceCount, buyBtn, result, loadingOverlay;
let numberSection, phoneNumber, requestId, numberStatus;
let timerBadge, countdown, cancelBtn, refundInfo, refundMessage;
let balanceBadge, userBalance;
let smsSection, smsFrom, smsMessage, smsCode;

// ✅ Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ DOM Loaded, initializing...');
    initializeElements();
    loadInitialData();
    setupEventListeners();
});

// Initialize all DOM elements
function initializeElements() {
    // Form elements
    countrySelect = document.getElementById('countrySelect');
    serviceSelect = document.getElementById('serviceSelect');
    countrySearch = document.getElementById('countrySearch');
    serviceSearch = document.getElementById('serviceSearch');
    serviceCount = document.getElementById('serviceCount');
    buyBtn = document.getElementById('buyBtn');
    result = document.getElementById('result');
    loadingOverlay = document.getElementById('loadingOverlay');
    
    // Number display elements
    numberSection = document.getElementById('numberSection');
    phoneNumber = document.getElementById('phoneNumber');
    requestId = document.getElementById('requestId');
    numberStatus = document.getElementById('numberStatus');
    timerBadge = document.getElementById('timerBadge');
    countdown = document.getElementById('countdown');
    cancelBtn = document.getElementById('cancelBtn');
    refundInfo = document.getElementById('refundInfo');
    refundMessage = document.getElementById('refundMessage');
    
    // Balance elements (FIX 3)
    balanceBadge = document.getElementById('balanceBadge');
    userBalance = document.getElementById('userBalance');
    
    // SMS display elements
    smsSection = document.getElementById('smsSection');
    smsFrom = document.getElementById('smsFrom');
    smsMessage = document.getElementById('smsMessage');
    smsCode = document.getElementById('smsCode');
    
    console.log('✅ All elements initialized');
}

// Setup event listeners
function setupEventListeners() {
    // Form submission
    document.getElementById('buyNumberForm').addEventListener('submit', handleBuyNumber);
    
    // Country change
    countrySelect.addEventListener('change', handleCountryChange);
    
    // Search inputs
    serviceSearch.addEventListener('input', handleServiceSearch);
    countrySearch.addEventListener('input', handleCountrySearch);
    
    console.log('✅ Event listeners attached');
}

// ===== LOAD DATA FUNCTIONS =====

// ✅ FIX 3: Load balance + countries
async function loadInitialData() {
    showLoading(true);
    
    try {
        // Load balance (FIX 3)
        await loadUserBalance();
        
        // Load countries
        await loadCountries();
        
        console.log('✅ Initial data loaded');
        
    } catch (error) {
        console.error('❌ Error loading data:', error);
        showError('Failed to load data. Please refresh the page.');
    } finally {
        showLoading(false);
    }
}

// ✅ FIX 3: Load User Balance
async function loadUserBalance() {
    try {
        if (!window.api || !window.api.wallet) {
            console.log('⚠️ API not loaded yet, skipping balance');
            return;
        }
        
        const balanceData = await window.api.wallet.getBalance();
        const balance = balanceData.balance || 0;
        
        userBalance.textContent = `₹${balance.toFixed(2)}`;
        balanceBadge.style.display = 'inline-block';
        
        console.log('✅ Balance loaded:', balance);
    } catch (error) {
        console.log('⚠️ Balance load failed (user may not be logged in):', error.message);
        // Don't show error - maybe user not logged in
    }
}

async function loadCountries() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/smsman/countries`);
        const data = await response.json();
        
        if (data.success && data.countries) {
            countries = data.countries;
            populateCountries();
            console.log(`✅ Loaded ${countries.length} countries`);
        } else {
            throw new Error('Failed to load countries');
        }
        
    } catch (error) {
        console.error('❌ Error loading countries:', error);
        showError('Failed to load countries.');
    }
}

async function loadServicesForCountry(countryId) {
    serviceSelect.innerHTML = '<option value="">🔄 Loading services...</option>';
    serviceSearch.disabled = true;
    serviceSearch.placeholder = 'Loading services...';
    serviceCount.textContent = '';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/smsman/services`);
        const data = await response.json();
        
        if (data.success && data.services && data.services.length > 0) {
            allServices = data.services;
            filteredServices = [...allServices];
            
            populateServices();
            updateServiceSearch();
            
            console.log(`✅ Loaded ${allServices.length} services`);
        } else {
            serviceSelect.innerHTML = '<option value="">❌ No services available</option>';
            allServices = [];
            filteredServices = [];
            serviceSearch.disabled = true;
        }
    } catch (error) {
        console.error('❌ Error loading services:', error);
        serviceSelect.innerHTML = '<option value="">❌ Error loading services</option>';
        allServices = [];
        filteredServices = [];
        serviceSearch.disabled = true;
    }
}

// ===== POPULATE FUNCTIONS =====

function populateCountries() {
    countrySelect.innerHTML = '<option value="">Select Country</option>';
    
    countries.forEach(country => {
        const option = document.createElement('option');
        option.value = country.id;
        option.textContent = `${country.title} (${country.code})`;
        countrySelect.appendChild(option);
    });
}

function populateServices() {
    serviceSelect.innerHTML = '<option value="">Select Service</option>';
    
    filteredServices.forEach(service => {
        const option = document.createElement('option');
        option.value = service.id;
        option.textContent = `${service.name} - ${service.display_price}`;
        serviceSelect.appendChild(option);
    });
    
    updateServiceCount();
}

function updateServiceSearch() {
    serviceSearch.disabled = false;
    serviceSearch.placeholder = 'Search services...';
    serviceSearch.value = '';
}

function updateServiceCount() {
    if (allServices.length > 0) {
        serviceCount.textContent = `Showing ${filteredServices.length} of ${allServices.length} services`;
    } else {
        serviceCount.textContent = '';
    }
}

// ===== EVENT HANDLERS =====

function handleCountryChange(e) {
    const countryId = parseInt(e.target.value);
    
    if (countryId) {
        loadServicesForCountry(countryId);
    } else {
        serviceSelect.innerHTML = '<option value="">Select country first...</option>';
        allServices = [];
        filteredServices = [];
        serviceSearch.disabled = true;
        serviceSearch.placeholder = 'Select country first...';
        serviceCount.textContent = '';
    }
}

function handleServiceSearch() {
    const searchTerm = serviceSearch.value.toLowerCase().trim();
    
    if (searchTerm.length < 1) {
        filteredServices = [...allServices];
    } else {
        filteredServices = allServices.filter(service => 
            service.name.toLowerCase().includes(searchTerm) ||
            service.display_price.toLowerCase().includes(searchTerm)
        );
    }
    
    populateServices();
    console.log(`🔍 Service search: "${searchTerm}" - Found ${filteredServices.length} services`);
}

function handleCountrySearch() {
    const searchTerm = countrySearch.value.toLowerCase();
    
    if (searchTerm.length < 1) {
        populateCountries();
        return;
    }
    
    const filteredCountries = countries.filter(country => 
        country.title.toLowerCase().includes(searchTerm) ||
        country.code.toLowerCase().includes(searchTerm)
    );
    
    countrySelect.innerHTML = '<option value="">Select Country</option>';
    
    filteredCountries.forEach(country => {
        const option = document.createElement('option');
        option.value = country.id;
        option.textContent = `${country.title} (${country.code})`;
        countrySelect.appendChild(option);
    });
}

// ===== BUY NUMBER FUNCTION =====

async function handleBuyNumber(e) {
    e.preventDefault();
    
    const countryId = parseInt(countrySelect.value);
    const serviceId = parseInt(serviceSelect.value);
    
    if (!countryId || !serviceId) {
        showError('Please select both country and service.');
        return;
    }
    
    buyBtn.disabled = true;
    buyBtn.textContent = '🔄 Purchasing...';
    result.innerHTML = '';
    
    // Hide previous results
    numberSection.style.display = 'none';
    smsSection.style.display = 'none';
    
    try {
        const token = localStorage.getItem('token');
        if (!token) {
            throw new Error('Please login first');
        }
        
        const response = await fetch(`${API_BASE_URL}/api/smsman/buy`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                application_id: serviceId,
                country_id: countryId
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Purchase failed');
        }
        
        if (data.success && data.number && data.request_id) {
            // Store purchase info
            currentPurchase = {
                number: data.number,
                request_id: data.request_id,
                country_code: data.country_code || '+91',
                display_number: data.display_number || data.number,
                service_id: serviceId,
                country_id: countryId,
                charged_amount: data.charged_amount,
                new_balance: data.new_balance
            };
            
            console.log('✅ Purchase successful:', currentPurchase);
            
            // Display the number (FIX 1)
            displayPurchasedNumber(data);
            
            // Update balance (FIX 3)
            if (data.new_balance !== undefined) {
                userBalance.textContent = `₹${data.new_balance.toFixed(2)}`;
            }
            
            // Start auto SMS checking (FIX 5)
            startSMSChecking();
            
            // Show refund info (FIX 4)
            showRefundInfo();
            
        } else {
            throw new Error(data.detail || data.message || 'Purchase failed');
        }
        
    } catch (error) {
        console.error('❌ Purchase error:', error);
        showError(`Purchase failed: ${error.message}`);
    } finally {
        buyBtn.disabled = false;
        buyBtn.textContent = '🛒 Buy Number';
    }
}

// ✅ FIX 1: Display number with country code
function displayPurchasedNumber(data) {
    phoneNumber.textContent = data.display_number || data.number;
    requestId.textContent = data.request_id;
    numberStatus.textContent = '⏳ Waiting for SMS';
    numberStatus.className = 'status-badge status-waiting';
    
    numberSection.style.display = 'block';
    
    showSuccess(`✅ Number purchased! Charged: ₹${data.charged_amount || 'N/A'}`);
}

// ===== SMS CHECKING FUNCTIONS =====

// ✅ FIX 5: Start SMS checking with timer
function startSMSChecking() {
    // Show timer
    timerBadge.style.display = 'inline-block';
    
    // Check immediately
    checkForSMS();
    
    // Then check every 5 seconds
    smsCheckInterval = setInterval(checkForSMS, 5000);
    
    // Start countdown timer
    startCountdown();
    
    // Stop after 5 minutes
    setTimeout(() => {
        stopSMSChecking();
        numberStatus.textContent = '⏱️ SMS Timeout';
        numberStatus.className = 'status-badge';
        numberStatus.style.background = '#f8d7da';
        numberStatus.style.color = '#721c24';
    }, 300000); // 5 minutes
}

// ✅ FIX 5: Countdown timer
function startCountdown() {
    secondsLeft = 5;
    countdown.textContent = secondsLeft;
    
    countdownInterval = setInterval(() => {
        secondsLeft--;
        if (secondsLeft <= 0) {
            secondsLeft = 5;
        }
        countdown.textContent = secondsLeft;
    }, 1000);
}

function stopSMSChecking() {
    if (smsCheckInterval) {
        clearInterval(smsCheckInterval);
        smsCheckInterval = null;
    }
    if (countdownInterval) {
        clearInterval(countdownInterval);
        countdownInterval = null;
    }
    timerBadge.style.display = 'none';
}

async function checkForSMS() {
    if (!currentPurchase) return;
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE_URL}/api/smsman/sms/${currentPurchase.request_id}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success && data.sms_received && data.sms_code) {
            // SMS received!
            displaySMS({
                code: data.sms_code,
                message: data.sms_text || `Your verification code: ${data.sms_code}`,
                from: data.sender || 'Service'
            });
            
            stopSMSChecking();
            
            numberStatus.textContent = '✅ SMS Received';
            numberStatus.className = 'status-badge status-completed';
            
            // ✅ FIX 4: Disable cancel after SMS
            disableCancelButton();
            
        } else if (data.status === 'waiting') {
            console.log('⏳ Still waiting for SMS...');
        }
        
    } catch (error) {
        console.error('❌ SMS check error:', error);
    }
}

// Manual SMS check (called from HTML button)
window.manualCheckSMS = async function() {
    console.log('🔄 Manual SMS check triggered');
    await checkForSMS();
};

function displaySMS(smsData) {
    smsFrom.textContent = smsData.from;
    smsMessage.textContent = smsData.message;
    smsCode.textContent = smsData.code;
    
    smsSection.style.display = 'block';
    
    showSuccess('🎉 SMS received! Your verification code is ready.');
}

// ===== CANCEL FUNCTION =====

// ✅ FIX 2 & FIX 4: Cancel number with refund (called from HTML button)
window.cancelNumber = async function() {
    if (!currentPurchase) {
        showError('No active purchase to cancel');
        return;
    }
    
    if (!confirm('Are you sure you want to cancel this number? You will get a refund if SMS not received yet.')) {
        return;
    }
    
    cancelBtn.disabled = true;
    cancelBtn.textContent = '🔄 Cancelling...';
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE_URL}/api/smsman/cancel/${currentPurchase.request_id}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Cancellation failed');
        }
        
        if (data.success) {
            stopSMSChecking();
            
            numberStatus.textContent = '❌ Cancelled';
            numberStatus.className = 'status-badge status-cancelled';
            
            // Update balance (FIX 3)
            if (data.new_balance !== undefined) {
                userBalance.textContent = `₹${data.new_balance.toFixed(2)}`;
            }
            
            showSuccess(`✅ ${data.message || 'Cancelled successfully!'} Refunded: ₹${data.refund_amount || 'N/A'}`);
            
            disableCancelButton();
            
        } else {
            throw new Error(data.detail || 'Cancellation failed');
        }
        
    } catch (error) {
        console.error('❌ Cancel error:', error);
        showError(`❌ ${error.message}`);
        cancelBtn.disabled = false;
        cancelBtn.textContent = '❌ Cancel Number';
    }
};

// ✅ FIX 4: Show refund info
function showRefundInfo() {
    refundInfo.style.display = 'block';
    refundMessage.textContent = '⚠️ You can cancel and get full refund if SMS not received yet.';
}

// ✅ FIX 4: Disable cancel button after SMS
function disableCancelButton() {
    cancelBtn.disabled = true;
    cancelBtn.textContent = '❌ Cannot Cancel';
    refundMessage.textContent = '❌ Cannot cancel - SMS already received or number cancelled.';
    refundInfo.style.background = '#f8d7da';
    refundInfo.style.borderColor = '#d63031';
    refundInfo.style.color = '#721c24';
}

// ===== UI HELPER FUNCTIONS =====

function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
}

function showError(message) {
    result.innerHTML = `<div class="error">❌ ${message}</div>`;
}

function showSuccess(message) {
    result.innerHTML = `<div class="success">✅ ${message}</div>`;
}

function showInfo(message) {
    result.innerHTML = `<div class="info">ℹ️ ${message}</div>`;
}

console.log('✅ Buy Number Script Loaded');
