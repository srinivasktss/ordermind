/**
 * Login page logic.
 *
 * Backend contract (users app):
 *   POST /users/login/  body: { username, password }
 *   - 200 OK            -> session cookie set, user is authenticated
 *   - 400/401 + JSON     -> { "detail": "Invalid Credentials" }
 *
 * On success the user is redirected to /orders/chat/.
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

const form = document.getElementById('login-form');
const errorBox = document.getElementById('login-error');
const submitBtn = document.getElementById('login-submit');
const btnLabel = submitBtn.querySelector('.btn-label');
const btnSpinner = submitBtn.querySelector('.btn-spinner');

function setLoading(isLoading) {
    submitBtn.disabled = isLoading;
    btnLabel.hidden = isLoading;
    btnSpinner.hidden = !isLoading;
}

function showError(message) {
    errorBox.textContent = message;
    errorBox.hidden = false;
}

function hideError() {
    errorBox.hidden = true;
}

form.addEventListener('submit', async (event) => {
    event.preventDefault();
    hideError();
    setLoading(true);

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    try {
        const response = await apiFetch('/users/login/', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });

        if (response.ok) {
            window.location.href = '/orders/chat/';
            return;
        }

        let message = 'Invalid username or password.';
        try {
            const data = await response.json();
            message = data.detail || message;
        } catch (_) {
            // Backend didn't return JSON — keep the default message.
        }
        showError(message);
    } catch (err) {
        showError('Could not reach the server. Please try again.');
    } finally {
        setLoading(false);
    }
});
