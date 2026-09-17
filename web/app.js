const API_URL = window.DIYA_API_URL || "http://localhost:8000";

const log = document.getElementById("log");
const form = document.getElementById("form");
const input = document.getElementById("input");

let sessionId = null;

function appendMessage(role, text) {
  const el = document.createElement("div");
  el.className = `msg ${role}`;
  el.textContent = text;
  log.appendChild(el);
  log.scrollTop = log.scrollHeight;
  return el;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  input.value = "";
  input.disabled = true;
  appendMessage("user", message);
  const pending = appendMessage("assistant", "...");

  try {
    const res = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId }),
    });
    if (!res.ok) throw new Error(`server returned ${res.status}`);
    const data = await res.json();
    sessionId = data.session_id;
    pending.textContent = data.reply;
  } catch (err) {
    pending.textContent = `Error talking to DIYA: ${err.message}`;
  } finally {
    input.disabled = false;
    input.focus();
  }
});
