// API Configuration
const API_BASE_URL = window.API_BASE_URL || 'https://brandotpofficial.onrender.com';
console.log('📱 SMSMan API:', API_BASE_URL);


const svc = document.getElementById("service"),
      srv = document.getElementById("server"),
      num = document.getElementById("num"),
      msg = document.getElementById("msg");
let oid = null;

const show = (t, c) => {
  msg.textContent = t;
  msg.className = `message ${c}`;
  msg.style.display = "block";
}

// Load all available services and countries (servers)
(async function loadMeta() {
 const meta = await fetch(`${API_BASE_URL}/api/smsman/meta`).then(r=>r.json());
  meta.services.forEach(s => svc.add(new Option(s.name, s.id)));
  meta.countries.forEach(c => srv.add(new Option(c.name, c.id)));
})();

document.getElementById("buyBtn").onclick = async () => {
  show("Buying...","success");
 const res = await fetch(`${API_BASE_URL}/api/smsman/buy`,{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({
      application_id: Number(svc.value),
      country_id: Number(srv.value)
    })
  });
  if(!res.ok){
    show("Failed to buy number","error");
    return;
  }
  const data = await res.json();
  if(!data.hasOwnProperty("request_id")){
    show(data.message || "Failed","error");
    return;
  }
  oid = data.request_id;
  num.textContent = data.number;
  show("Number active, wait OTP","success");
  document.getElementById("otpBtn").disabled = false;
  document.getElementById("cancelBtn").disabled = false;
};

document.getElementById("otpBtn").onclick = async () => {
  if(!oid) return;
 const data = await fetch(`${API_BASE_URL}/api/smsman/sms/${oid}`).then(r=>r.json());
  let code = "";
  if(Array.isArray(data.sms) && data.sms.length){
    code = data.sms[0].code || "";
  }
  show(code ? `OTP: ${code}` : "Still waiting...", "success");
};

document.getElementById("cancelBtn").onclick = async () => {
  if(!oid) return;
 await fetch(`${API_BASE_URL}/api/smsman/cancel/${oid}`,{method:"POST"});
  show("Cancelled","success");
  oid = null;
  num.textContent = "–";
  document.getElementById("otpBtn").disabled = true;
  document.getElementById("cancelBtn").disabled = true;
};

