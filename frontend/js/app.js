/* LibroBot — Pure ML-Driven UI Client (No rule-based keyword matching in frontend) */
let isLoading = false;
const FALLBACK = 'Sorry, I could not understand your query. Kindly rephrase it and try again.';
const API_BASE = 'http://127.0.0.1:5000';

// Session ID tracks multi-turn calculator prompts (e.g., overdue days -> number of books) on the backend
const SESSION_ID = 'sess_' + Math.random().toString(36).slice(2, 11);

document.addEventListener('DOMContentLoaded', () => {
  renderQuickChips(document.getElementById('quickQueryDock'));
});

function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

function sendChip(text) {
  document.getElementById('userInput').value = text;
  sendMessage();
}

function renderQuickChips(container) {
  if (!container) return;
  container.innerHTML = '';
  QUICK_CHIPS.forEach(item => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'chip';
    b.textContent = item.label;
    b.addEventListener('click', () => sendChip(item.text));
    container.appendChild(b);
  });
}

function addMessage(role, text, showRelated = false) {
  const box = document.getElementById('chatBox');
  document.getElementById('welcomeCard')?.remove();
  const msg = document.createElement('div');
  msg.className = `msg ${role === 'user' ? 'user' : 'bot'}`;
  const av = document.createElement('div');
  av.className = `avatar ${role === 'user' ? 'user-av' : 'bot'}`;
  av.textContent = role === 'user' ? '👤' : '📚';
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.innerHTML = formatText(text);

  if (role === 'bot' && showRelated) {
    const h = document.createElement('p');
    h.className = 'suggestion-heading';
    h.textContent = 'You can also try one of these related questions:';
    bubble.appendChild(h);
    const rel = document.createElement('div');
    rel.className = 'quick-chips related-chips';
    renderQuickChips(rel);
    bubble.appendChild(rel);
  }
  msg.append(av, bubble);
  box.appendChild(msg);
  box.scrollTop = box.scrollHeight;
}

function formatText(value) {
  const links = [];
  const keep = html => { links.push(html); return `\u0000${links.length - 1}\u0000`; };
  let t = String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  t = t.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, (m, label, url) => keep(`<a href="${url}" target="_blank" rel="noopener noreferrer">${label}</a>`));
  t = t.replace(/(https?:\/\/[^\s<)]+[^\s<).,;])/g, (m, url) => keep(`<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`));
  t = t.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  const lines = t.split('\n').map(x => x.trim()).filter(Boolean);
  let out = '', list = false, table = [];
  const flushList = () => { if (list) { out += '</ul>'; list = false; } };
  const flushTable = () => {
    if (!table.length) return;
    const rows = table.map(r => r.split('|').slice(1, -1).map(c => c.trim())).filter(r => !r.every(c => /^:?-{2,}:?$/.test(c)));
    out += '<table>' + rows.map((r, i) => '<tr>' + r.map(c => i === 0 ? `<th>${c}</th>` : `<td>${c}</td>`).join('') + '</tr>').join('') + '</table>';
    table = [];
  };
  for (const line of lines) {
    if (line.startsWith('|')) { flushList(); table.push(line); continue; }
    flushTable();
    if (/^[-•]\s+/.test(line)) {
      if (!list) { out += '<ul>'; list = true; }
      out += `<li>${line.replace(/^[-•]\s+/, '')}</li>`;
      continue;
    }
    flushList();
    if (line.startsWith('### ')) out += `<h4>${line.slice(4)}</h4>`;
    else if (line.startsWith('~ ')) out += `<p class="src">${line.slice(2)}</p>`;
    else out += `<p>${line}</p>`;
  }
  flushList();
  flushTable();
  return out.replace(/\u0000(\d+)\u0000/g, (m, i) => links[+i]);
}

function showTyping() {
  const box = document.getElementById('chatBox');
  const el = document.createElement('div');
  el.className = 'typing-indicator';
  el.id = 'typingIndicator';
  el.innerHTML = '<div class="avatar bot">📚</div><div class="typing-dots"><span></span><span></span><span></span></div>';
  box.appendChild(el);
  box.scrollTop = box.scrollHeight;
}

function removeTyping() {
  document.getElementById('typingIndicator')?.remove();
}

const PENDING_UI = {
  fine_days: {
    placeholder: 'Enter number of overdue days (e.g. 12) or due date (DD-MM-YYYY)…',
    hint: '⌨️ Waiting for the number of overdue days — type a number, or ask something else to skip.'
  },
  fine_books: {
    placeholder: 'Enter number of overdue books (e.g. 2)…',
    hint: '⌨️ Optional: number of overdue books — type a number, or ask something else to skip.'
  },
  due_date: {
    placeholder: 'Enter the issue date (DD-MM-YYYY)…',
    hint: '⌨️ Waiting for the issue date — type it as DD-MM-YYYY, or ask something else to skip.'
  }
};

function updatePendingUI(pendingMode) {
  const input = document.getElementById('userInput');
  const hint = document.getElementById('modeHint');
  if (pendingMode && PENDING_UI[pendingMode]) {
    input.placeholder = PENDING_UI[pendingMode].placeholder;
    input.classList.add('awaiting');
    hint.textContent = PENDING_UI[pendingMode].hint;
    hint.classList.add('on');
  } else {
    input.placeholder = 'Ask about the MANIT Central Library…';
    input.classList.remove('awaiting');
    hint.classList.remove('on');
    hint.textContent = '';
  }
}

async function queryMLBackend(raw) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: raw, session_id: SESSION_ID })
  });
  if (!res.ok) throw new Error(`Backend HTTP ${res.status}`);
  return await res.json();
}

async function sendMessage() {
  if (isLoading) return;
  const input = document.getElementById('userInput');
  const text = input.value.trim();
  if (!text) return;

  input.value = '';
  input.style.height = 'auto';
  isLoading = true;
  document.getElementById('sendBtn').disabled = true;
  addMessage('user', text);
  showTyping();

  try {
    const data = await queryMLBackend(text);
    removeTyping();
    updatePendingUI(data.pending_mode || null);
    const answer = data.response || FALLBACK;
    addMessage('bot', answer, answer === FALLBACK);
  } catch (err) {
    console.error(err);
    removeTyping();
    updatePendingUI(null);
    addMessage('bot', 'Unable to connect to the local ML server at **http://127.0.0.1:5000**. Please ensure `python backend/app.py` is running.');
  } finally {
    isLoading = false;
    document.getElementById('sendBtn').disabled = false;
    input.focus();
  }
}
