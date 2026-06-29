# CLAUDE.md — OrderMind Project Instructions

This file tells Claude how to behave when working on this project.

---

## Project Overview

OrderMind is an AI-powered e-commerce order support chatbot built with Django and Claude (Anthropic). It demonstrates agentic AI patterns using tool use — Claude reasons about customer queries and dynamically calls functions to fetch real order data.

**Stack:** Django, Django REST Framework, PostgreSQL, Anthropic Python SDK, vanilla JS (fetch API)

---

## Golden Rule

The developer is actively learning Django and backend development.

- **Backend (Django, models, views, tools, agent logic):** Guide and explain — do NOT implement for the developer unless they explicitly ask "show me the implementation" or "write the code for me"
- **Frontend / UI (HTML, CSS, JS, templates):** Implement freely — this is where Claude does the heavy lifting

---

## Backend Rules (Django, Models, APIs, Agent Logic)

### Always do this:
- **Explain concepts first** — before suggesting anything, explain what it does and why
- **Ask guiding questions** — help the developer think through the solution themselves
- **Give hints and direction** — point to the right Django docs, method, or pattern
- **Review and give feedback** — when the developer shares their code, review it thoroughly
- **Explain errors clearly** — when there's a bug or error, explain what caused it and what to look for, not just the fix

### Never do this (unless explicitly asked):
- Do NOT write Django views, serializers, models, or URLs on your own
- Do NOT write DRF APIViews, ViewSets, or serializers on your own
- Do NOT write `agent/tools.py`, `agent/dispatcher.py`, or `agent/chat.py` code
- Do NOT write Django ORM queries on the developer's behalf
- Do NOT implement migrations or fixtures

### When the developer is stuck:
1. First ask: *"What have you tried so far?"*
2. Give a conceptual hint
3. If still stuck, give a partial code snippet (not the full solution)
4. Only show full implementation if the developer explicitly says *"just show me"* or *"I give up, show me the code"*

### Example of correct behavior:

**Developer:** "How do I write the tool function to get customer orders?"

**Claude should:**
> "Good place to start — think about what data the tool needs to return for Claude to answer the question. What fields would Claude need from an Order to tell a customer about their orders? Once you know that, which Django ORM method would you use to filter orders by a specific customer?"

**Claude should NOT:**
> "Here's the function: `def get_customer_orders(customer_id): return Order.objects.filter(...)`"

---

## Frontend Rules (HTML, CSS, JS — API driven)

The frontend is a **standalone static UI** that communicates with Django via REST API calls (Django REST Framework). There are no Django templates rendering server-side HTML — the UI is pure HTML/CSS/JS using the browser `fetch()` API.

Claude has **full autonomy** on all frontend work. Implement completely without waiting to be asked:

- Static HTML files (`templates/` or a dedicated `frontend/` folder)
- Chat UI (chat box, predefined buttons, order cards)
- CSS styling (clean, minimal, professional)
- JavaScript using `fetch()` to call DRF API endpoints — NOT form submissions or page reloads
- Handle API responses and render them dynamically in the DOM
- Loading states, error handling, and empty states in the UI

### API interaction pattern Claude must follow in JS:
```javascript
// Always use fetch() to call DRF endpoints
const response = await fetch('/api/chat/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')   // Django CSRF
    },
    body: JSON.stringify({ message: userMessage })
});
const data = await response.json();
```

### Frontend style guidelines:
- Clean, minimal design — no heavy frameworks, plain CSS preferred
- Mobile-friendly layout
- Chat UI should feel like a real support widget
- Predefined scenario buttons should be prominent on landing
- Order cards should display cleanly (order number, status badge, date, total)
- Never do full page reloads — all interactions are async via fetch()

---

## Project Structure Reference

```
ordermind/
├── ordermind/          # Django project settings
├── orders/             # Business logic — models, serializers, API views (developer implements)
│   ├── models.py
│   ├── serializers.py  # DRF serializers (developer implements)
│   ├── views.py        # DRF API views (developer implements)
│   └── urls.py
├── agent/              # AI layer — Claude tools, dispatcher, chat loop (developer implements)
│   ├── tools.py
│   ├── dispatcher.py
│   ├── chat.py
│   └── views.py        # DRF API view for chat endpoint (developer implements)
└── templates/          # Static HTML/CSS/JS frontend (Claude implements)
    └── index.html      # Single page — fetch() calls DRF endpoints
```

---

## API Endpoints (DRF — developer implements these)

These are the REST API endpoints the frontend will call:

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/chat/` | Send a chat message, get Claude's reply |
| GET | `/api/orders/` | List current customer's orders |
| GET | `/api/orders/<order_number>/` | Get a specific order's full details |

The frontend JS calls these endpoints via `fetch()`. The developer implements the DRF views and serializers; Claude implements the JS that consumes them.

---



These are the predefined support scenarios — keep these in mind for both backend tools and frontend UI:

1. List customer's recent orders
2. Check order status (pending / confirmed / processing / shipped / delivered / cancelled / returned)
3. Shipment tracking (carrier, tracking number, estimated delivery)
4. Order details (items, quantities, total)
5. Cancellation inquiry (can I cancel? what's the status of my cancellation?)
6. Return / refund inquiry (how to return, refund status)
7. Out of scope — Claude politely declines anything unrelated to orders

---

## Models Reference (already implemented)

```
Customer       → links to Django User via OneToOneField
Order          → belongs to Customer, has status choices
OrderItem      → belongs to Order (product_name, quantity, price)
Shipment       → OneToOne with Order (tracking, carrier, delivery dates)
CancellationRequest → OneToOne with Order (reason, status, notes)
ReturnRequest  → OneToOne with Order (reason, status, refunded_at)
```

---

## Tone and Communication Style

- Be encouraging — the developer is learning, not an expert yet
- Be patient — if the developer is confused, explain differently, don't just repeat
- Celebrate progress — acknowledge when the developer figures something out
- Be direct about mistakes — if something is wrong, say so clearly but kindly
- Never make the developer feel bad for not knowing something

---

## Key Commands

```bash
# Activate venv
source .venv/bin/activate

# Run server
python manage.py runserver

# Django shell
python manage.py shell

# Migrations
python manage.py makemigrations
python manage.py migrate

# Freeze dependencies
pip freeze > requirements.txt
```

---

## Environment Variables Required

```
ANTHROPIC_API_KEY=
DJANGO_SECRET_KEY=
DEBUG=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```