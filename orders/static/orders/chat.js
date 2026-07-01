/**
 * Chat page logic.
 *
 * Backend contract (chats app):
 *   POST /chats/  body: { messages: [{role, content}, ...] }  <- full history each time
 *   -> 200 OK + JSON: { "reply": "<text Claude said>", "orders": [ ... ] (optional) }
 *   -> 401            if the session isn't authenticated (redirects to /users/login/)
 *
 * Backend contract (users app):
 *   POST /users/logout -> 200 OK, clears the session
 *
 * Conversation history is kept in-memory only. Refreshing the page starts a new chat.
 * Order objects (optional "orders" field) are rendered as cards via
 * renderOrderCard() from common.js — expected shape: order_number,
 * status, created_at, total.
 */

// In-memory conversation history in Anthropic message format.
// Cleared on every page load (refresh = new chat).
const conversationHistory = [];

const messagesEl = document.getElementById('messages');
const form = document.getElementById('chat-form');
const input = document.getElementById('chat-input');
const sendBtn = document.getElementById('chat-send');
const scenarioBar = document.getElementById('scenario-bar');
const logoutBtn = document.getElementById('logout-btn');

function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function appendMessage(text, sender) {
    const wrapper = document.createElement('div');
    wrapper.className = `message message-${sender}`;
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = text;
    wrapper.appendChild(bubble);
    messagesEl.appendChild(wrapper);
    scrollToBottom();
    return wrapper;
}

function appendOrders(orders) {
    const wrapper = document.createElement('div');
    wrapper.className = 'message message-bot';
    const list = document.createElement('div');
    list.className = 'order-card-list';
    orders.forEach((order) => list.appendChild(renderOrderCard(order)));
    wrapper.appendChild(list);
    messagesEl.appendChild(wrapper);
    scrollToBottom();
}

function appendTypingIndicator() {
    const wrapper = document.createElement('div');
    wrapper.className = 'message message-bot message-typing';
    wrapper.innerHTML = '<div class="message-bubble"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>';
    messagesEl.appendChild(wrapper);
    scrollToBottom();
    return wrapper;
}

async function sendMessage(text) {
    // Add user message to history before sending
    conversationHistory.push({ role: 'user', content: text });

    appendMessage(text, 'user');
    input.value = '';
    setInputDisabled(true);
    const typingIndicator = appendTypingIndicator();

    try {
        const response = await apiFetch('/chats/', {
            method: 'POST',
            body: JSON.stringify({ messages: conversationHistory }),
        });

        if (response.status === 401) {
            window.location.href = '/users/login/';
            return;
        }

        const data = await response.json();
        typingIndicator.remove();

        if (!response.ok) {
            // Remove the user message from history so it can be retried
            conversationHistory.pop();
            appendMessage(data.error || 'Something went wrong. Please try again.', 'bot');
            return;
        }

        // Add assistant reply to history to maintain context on next send
        conversationHistory.push({ role: 'assistant', content: data.reply || '' });

        appendMessage(data.reply || '', 'bot');
        if (Array.isArray(data.orders) && data.orders.length > 0) {
            appendOrders(data.orders);
        }
    } catch (err) {
        typingIndicator.remove();
        // Remove the user message from history so it can be retried
        conversationHistory.pop();
        appendMessage('Could not reach the server. Please try again.', 'bot');
    } finally {
        setInputDisabled(false);
        input.focus();
    }
}

function setInputDisabled(disabled) {
    input.disabled = disabled;
    sendBtn.disabled = disabled;
}

form.addEventListener('submit', (event) => {
    event.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    sendMessage(text);
});

scenarioBar.addEventListener('click', (event) => {
    const btn = event.target.closest('.scenario-btn');
    if (!btn) return;
    sendMessage(btn.dataset.message);
});

logoutBtn.addEventListener('click', async () => {
    try {
        await apiFetch('/users/logout', { method: 'POST' });
    } finally {
        window.location.href = '/users/login/';
    }
});
