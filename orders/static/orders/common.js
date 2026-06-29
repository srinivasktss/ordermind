/**
 * Shared helpers used by both the login and chat pages.
 */

// Reads a cookie value by name (used to grab Django's CSRF token).
function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
}

// Wraps fetch() with JSON headers + CSRF token already attached.
async function apiFetch(url, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
        ...(options.headers || {}),
    };
    return fetch(url, { ...options, headers });
}

// Renders an order object as a status-badged card. Adjust the field
// names here once the order serializer's exact shape is known.
function renderOrderCard(order) {
    const card = document.createElement('div');
    card.className = 'order-card';
    card.innerHTML = `
        <div class="order-card-row">
            <span class="order-number">#${order.order_number ?? ''}</span>
            <span class="status-badge status-${(order.status ?? '').toLowerCase()}">${order.status ?? ''}</span>
        </div>
        <div class="order-card-row order-card-meta">
            <span>${order.created_at ?? ''}</span>
            <span>${order.total ?? ''}</span>
        </div>
    `;
    return card;
}
