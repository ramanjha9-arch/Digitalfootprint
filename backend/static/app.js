// Same-origin: frontend is served by the same Flask app as the API,
// so no separate backend URL is needed.
const BACKEND_URL = "";

async function checkPhone() {
  const number = document.getElementById("phoneInput").value.trim();
  const out = document.getElementById("phoneResult");
  const btn = document.getElementById("phoneBtn");
  if (!number) return;

  btn.disabled = true; btn.textContent = "Scanning...";
  out.classList.add("show");
  out.textContent = "Running PhoneInfoga scan...";

  try {
    const res = await fetch(`${BACKEND_URL}/api/phone-lookup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ number })
    });
    const data = await res.json();
    if (data.error) {
      out.textContent = `Error: ${data.error}`;
    } else {
      let text = JSON.stringify(data.result, null, 2);
      text += "\n\n--- Suggestions ---\n";
      (data.suggestions || []).forEach(s => text += `• ${s}\n`);
      out.textContent = text;
    }
  } catch (e) {
    out.textContent = `Could not reach backend. Is BACKEND_URL set correctly in app.js?\n${e}`;
  } finally {
    btn.disabled = false; btn.textContent = "Check";
  }
}

async function checkEmail() {
  const email = document.getElementById("emailInput").value.trim();
  const out = document.getElementById("emailResult");
  const btn = document.getElementById("emailBtn");
  if (!email) return;

  btn.disabled = true; btn.textContent = "Checking...";
  out.classList.add("show");

  try {
    const res = await fetch(`${BACKEND_URL}/api/email-info`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email })
    });
    const data = await res.json();
    let html = "Manual breach checks (free, no key needed):\n";
    data.manual_checks.forEach(c => {
      html += `  → ${c.name}: ${c.url}\n`;
    });
    html += "\nCleanup resources:\n";
    data.cleanup_resources.forEach(c => {
      html += `  → ${c.name}: ${c.url}\n`;
    });
    out.textContent = html;
  } catch (e) {
    out.textContent = `Could not reach backend.\n${e}`;
  } finally {
    btn.disabled = false; btn.textContent = "Check";
  }
}

async function checkUsername() {
  const username = document.getElementById("userInput").value.trim();
  const out = document.getElementById("userResult");
  const btn = document.getElementById("userBtn");
  if (!username) return;

  btn.disabled = true; btn.textContent = "Scanning...";
  out.classList.add("show");
  out.textContent = "Checking platforms...";

  try {
    const res = await fetch(`${BACKEND_URL}/api/username-check`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username })
    });
    const data = await res.json();
    let html = `<ul class="checklist">`;
    data.results.forEach(r => {
      let tagClass = r.likely_exists === true ? "found" : r.likely_exists === false ? "clear" : "unknown";
      let tagText = r.likely_exists === true ? "found" : r.likely_exists === false ? "not found" : "unknown";
      html += `<li><span>${r.site}</span><a href="${r.url}" target="_blank" class="tag ${tagClass}">${tagText}</a></li>`;
    });
    html += `</ul>`;
    out.innerHTML = html;
  } catch (e) {
    out.textContent = `Could not reach backend.\n${e}`;
  } finally {
    btn.disabled = false; btn.textContent = "Check";
  }
}
