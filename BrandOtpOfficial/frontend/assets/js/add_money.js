/* ---------- Add Money (Pay0 only) ---------- */
/* API Configuration */
const API_BASE_URL = window.API_BASE_URL || 'https://brandotpofficial.onrender.com';
console.log('💰 Add Money - Using API:', API_BASE_URL);

/* ---------- Add Money (Pay0 only) ---------- */

const form   = document.getElementById("addMoneyForm");
const amount = document.getElementById("amount");
const mobile = document.getElementById("mobile_number");
const msgBox = document.getElementById("message");
const btn    = document.getElementById("addMoneyBtn");

/* quick-fill buttons */
function setAmount(v){
  amount.value = v;
  amount.focus();
}

/* show / hide message */
function showMessage(text,type){
  msgBox.textContent = text;
  msgBox.className   = `message ${type}`;
  msgBox.style.display = "block";
}
function clearMessage(){ msgBox.style.display="none"; }

/* submit handler */
form.addEventListener("submit", async e=>{
  e.preventDefault();
  clearMessage();
  btn.disabled = true;

  try{
    /* basic client-side validation */
    const amt = parseFloat(amount.value);
    if(isNaN(amt)||amt<50||amt>5000) throw new Error("Enter amount ₹50–₹5 000");
    if(!/^\d{10}$/.test(mobile.value)) throw new Error("Enter valid 10-digit mobile");

    /* hit FastAPI */
    const res = await fetch(`${API_BASE_URL}/api/payments/pay0/order`,{
      method:"POST",
      headers:{ "Content-Type":"application/json" },
      body: JSON.stringify({ mobile:mobile.value, amount:amt })
    });

    if(!res.ok){
      const err = await res.json();
      throw new Error(err.detail || "Gateway error");
    }
    const {payment_url} = await res.json();
    /* redirect */
    window.location.href = payment_url;

  }catch(err){
    showMessage(err.message||"Payment error","error");
  }finally{
    btn.disabled = false;
  }
});
