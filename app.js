const RASA_ENDPOINT = window.RASA_ENDPOINT || "http://localhost:5005/webhooks/rest/webhook";
const SENDER_ID = `eco-user-${Math.random().toString(36).slice(2)}`;

const messages = document.querySelector("#messages");
const form = document.querySelector("#chat-form");
const input = document.querySelector("#message-input");

function addMessage(role, html) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;
  wrapper.innerHTML = html;
  messages.appendChild(wrapper);
  messages.scrollTop = messages.scrollHeight;
}

function escapeHtml(text) {
  return String(text || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderButtons(buttons) {
  if (!buttons || buttons.length === 0) return "";
  return `<div class="quick-actions">${buttons.map(btn => `<button data-payload='${escapeHtml(btn.payload)}'>${escapeHtml(btn.title)}</button>`).join("")}</div>`;
}

function renderCustom(custom) {
  if (!custom) return "";
  if (custom.type === "carbon_card") {
    const rows = custom.items.map(item => `<li><span>${escapeHtml(item.label)}</span><strong>${escapeHtml(item.value)}</strong></li>`).join("");
    return `<article class="card ${escapeHtml(custom.band)}"><h3>${escapeHtml(custom.title)}</h3><ul>${rows}</ul><p class="small">${escapeHtml(custom.disclaimer)}</p></article>`;
  }
  if (custom.type === "result_cards") {
    const cards = custom.cards.map(card => {
      const metrics = Object.entries(card.metrics || {}).map(([k, v]) => `<li><span>${escapeHtml(k)}</span><strong>${escapeHtml(v)}</strong></li>`).join("");
      return `<article class="card ${escapeHtml(card.band)}"><h3>${escapeHtml(card.title)}</h3><p class="subtitle">${escapeHtml(card.subtitle)}</p><ul>${metrics}</ul><p>${escapeHtml(card.recommendation)}</p></article>`;
    }).join("");
    return `<div class="cards"><h3>${escapeHtml(custom.title)}</h3>${cards}</div>`;
  }
  if (custom.type === "handover") {
    const rows = Object.entries(custom.summary || {}).map(([k, v]) => `<li><span>${escapeHtml(k.replaceAll("_", " "))}</span><strong>${escapeHtml(JSON.stringify(v))}</strong></li>`).join("");
    return `<article class="handover"><h3>${escapeHtml(custom.title)}</h3><p>Conversation context is ready for advisor review.</p><ul>${rows}</ul></article>`;
  }
  return `<pre>${escapeHtml(JSON.stringify(custom, null, 2))}</pre>`;
}

async function sendMessage(message, displayText = null) {
  const trimmed = message.trim();
  if (!trimmed) return;
  const shownText = displayText || trimmed;
  addMessage("user", `<p>${escapeHtml(shownText)}</p>`);
  input.value = "";
  try {
    const response = await fetch(RASA_ENDPOINT, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ sender: SENDER_ID, message: trimmed })
    });
    const data = await response.json();
    if (!data.length) {
      addMessage("bot", `<p>I did not receive a response from the bot. Check that Rasa is running.</p>`);
      return;
    }
    data.forEach(msg => {
      const text = msg.text ? `<p>${escapeHtml(msg.text)}</p>` : "";
      const buttons = renderButtons(msg.buttons);
      const custom = renderCustom(msg.custom);
      addMessage("bot", `<strong>Eco-Travel Advisor</strong>${text}${buttons}${custom}`);
    });
  } catch (error) {
    addMessage("bot error", `<p>Connection error. Start Rasa with <code>rasa run --enable-api --cors "*"</code>.</p>`);
  }
}

form.addEventListener("submit", event => {
  event.preventDefault();
  sendMessage(input.value);
});

document.addEventListener("click", event => {
  const button = event.target.closest("button[data-payload]");
  if (button) sendMessage(button.dataset.payload, button.textContent);
});
