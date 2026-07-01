import json
from orders.models import Order

# ── Tool schemas (what Claude sees) ──────────────────────────────────────────
# customer_id is NOT in any schema — it is injected server-side from the
# authenticated session so Claude can never be tricked into querying
# another customer's data.

TOOLS = [
    {
        "name": "get_recent_orders",
        "description": (
            "Returns the customer's most recent orders. Use this when the "
            "customer asks to see their orders or order history."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of orders to return. Defaults to 5.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "get_order_status",
        "description": (
            "Returns the current status of a specific order. Use when the "
            "customer asks about the status of a particular order."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_number": {
                    "type": "string",
                    "description": "The order number, e.g. ORD-123.",
                }
            },
            "required": ["order_number"],
        },
    },
    {
        "name": "get_shipment_tracking",
        "description": (
            "Returns shipment tracking details including carrier, tracking "
            "number, and estimated delivery date."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_number": {
                    "type": "string",
                    "description": "The order number to get shipment info for.",
                }
            },
            "required": ["order_number"],
        },
    },
    {
        "name": "get_order_details",
        "description": (
            "Returns the full details of an order including all items, "
            "quantities, and prices."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_number": {
                    "type": "string",
                    "description": "The order number to get details for.",
                }
            },
            "required": ["order_number"],
        },
    },
    {
        "name": "get_cancellation_status",
        "description": (
            "Returns cancellation request details for an order. Use when the "
            "customer asks about cancelling an order or checking a cancellation."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_number": {
                    "type": "string",
                    "description": "The order number to check cancellation status for.",
                }
            },
            "required": ["order_number"],
        },
    },
    {
        "name": "get_return_status",
        "description": (
            "Returns return or refund request details for an order. Use when "
            "the customer asks about returning an item or checking refund status."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_number": {
                    "type": "string",
                    "description": "The order number to check return or refund status for.",
                }
            },
            "required": ["order_number"],
        },
    },
]

# ── DB query functions ────────────────────────────────────────────────────────

def _get_order(customer_id, order_number):
    """Fetch an order that belongs to this customer, or None."""
    try:
        return Order.objects.select_related('customer').get(
            order_number=order_number,
            customer__id=customer_id,
        )
    except Order.DoesNotExist:
        return None


def get_recent_orders(customer_id, limit=5, **_):
    orders = Order.objects.filter(customer__id=customer_id).order_by('-created_at')[:limit]
    if not orders:
        return 'No orders found.'
    return json.dumps([
        {
            'order_number': o.order_number,
            'status': o.status,
            'total_amount': str(o.total_amount),
            'created_at': o.created_at.strftime('%Y-%m-%d'),
        }
        for o in orders
    ])


def get_order_status(customer_id, order_number, **_):
    order = _get_order(customer_id, order_number)
    if not order:
        return f'No order found with number {order_number}.'
    return json.dumps({
        'order_number': order.order_number,
        'status': order.status,
        'updated_at': order.updated_at.strftime('%Y-%m-%d %H:%M'),
    })


def get_shipment_tracking(customer_id, order_number, **_):
    order = _get_order(customer_id, order_number)
    if not order:
        return f'No order found with number {order_number}.'
    try:
        s = order.shipment
    except Exception:
        return f'No shipment record found for order {order_number} yet.'
    return json.dumps({
        'order_number': order.order_number,
        'carrier': s.carrier,
        'tracking_number': s.tracking_number,
        'status': s.status,
        'shipped_at': s.shipped_at.strftime('%Y-%m-%d') if s.shipped_at else None,
        'estimated_delivery': str(s.estimated_delivery) if s.estimated_delivery else None,
        'delivered_at': s.delivered_at.strftime('%Y-%m-%d') if s.delivered_at else None,
    })


def get_order_details(customer_id, order_number, **_):
    order = _get_order(customer_id, order_number)
    if not order:
        return f'No order found with number {order_number}.'
    return json.dumps({
        'order_number': order.order_number,
        'status': order.status,
        'created_at': order.created_at.strftime('%Y-%m-%d'),
        'total_amount': str(order.total_amount),
        'items': [
            {
                'product_name': i.product_name,
                'quantity': i.quantity,
                'price': str(i.price),
                'subtotal': str(i.subtotal),
            }
            for i in order.items.all()
        ],
    })


def get_cancellation_status(customer_id, order_number, **_):
    order = _get_order(customer_id, order_number)
    if not order:
        return f'No order found with number {order_number}.'
    try:
        c = order.cancellation
    except Exception:
        return f'No cancellation request found for order {order_number}.'
    return json.dumps({
        'order_number': order.order_number,
        'order_status': order.status,
        'cancellation_status': c.status,
        'reason': c.reason,
        'notes': c.notes,
        'requested_at': c.requested_at.strftime('%Y-%m-%d'),
        'resolved_at': c.resolved_at.strftime('%Y-%m-%d') if c.resolved_at else None,
    })


def get_return_status(customer_id, order_number, **_):
    order = _get_order(customer_id, order_number)
    if not order:
        return f'No order found with number {order_number}.'
    try:
        r = order.return_request
    except Exception:
        return f'No return request found for order {order_number}.'
    return json.dumps({
        'order_number': order.order_number,
        'return_status': r.status,
        'reason': r.reason,
        'notes': r.notes,
        'requested_at': r.requested_at.strftime('%Y-%m-%d'),
        'refunded_at': r.refunded_at.strftime('%Y-%m-%d') if r.refunded_at else None,
    })


# ── Dispatcher ────────────────────────────────────────────────────────────────

_TOOL_FUNCTIONS = {
    'get_recent_orders':      get_recent_orders,
    'get_order_status':       get_order_status,
    'get_shipment_tracking':  get_shipment_tracking,
    'get_order_details':      get_order_details,
    'get_cancellation_status': get_cancellation_status,
    'get_return_status':      get_return_status,
}


def dispatch_tool(tool_name, tool_input, customer_id):
    """Look up the tool by name, inject customer_id, and return the result."""
    func = _TOOL_FUNCTIONS.get(tool_name)
    if not func:
        return f'Unknown tool: {tool_name}'
    return func(customer_id=customer_id, **tool_input)
