from .client import CLIENT, MODEL
from .tools import TOOLS, dispatch_tool

SYSTEM_PROMPT = """You are OrderMind, a helpful customer support assistant for an e-commerce store.
You help customers with questions about their orders, shipments, cancellations, and returns.
Always use the available tools to fetch real data before answering — never guess or make up order details.
If a customer asks about something unrelated to orders, politely let them know you can only help with order-related queries."""


def handle_chat_request(messages, customer_id):
    """
    Runs the agentic loop:
      1. Call Claude with the full conversation history + tool definitions.
      2. If Claude wants a tool, run it against the DB and feed the result back.
      3. Repeat until Claude returns a final text reply (stop_reason == 'end_turn').

    Args:
        messages (list): Conversation history in Anthropic format
                         [{'role': 'user'|'assistant', 'content': '...'}]
        customer_id (int): PK of the authenticated customer — injected into
                           every tool call so Claude can never query another
                           customer's data.

    Returns:
        str: Claude's final plain-text reply.
    """
    working_messages = list(messages)

    while True:
        response = CLIENT.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=working_messages,
        )

        # Claude has a final answer — exit the loop
        if response.stop_reason == 'end_turn':
            return response.content[0].text

        # Claude wants to call one or more tools
        if response.stop_reason == 'tool_use':
            # 1. Append Claude's response (contains the tool_use block) to history
            working_messages.append({
                'role': 'assistant',
                'content': response.content,
            })

            # 2. Run each requested tool and collect results
            tool_results = []
            for block in response.content:
                if block.type != 'tool_use':
                    continue

                result = dispatch_tool(block.name, block.input, customer_id)

                tool_results.append({
                    'type': 'tool_result',
                    'tool_use_id': block.id,
                    'content': result,
                })

            # 3. Feed all results back as a single user message, then loop
            working_messages.append({
                'role': 'user',
                'content': tool_results,
            })
