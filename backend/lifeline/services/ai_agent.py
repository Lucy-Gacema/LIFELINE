import json
import re
import uuid
from typing import Optional
from sqlalchemy.orm import Session
from lifeline.core.config import settings
from lifeline.schemas.assistant import AssistantMessageIn, AssistantMessageOut, ProposedAction
from lifeline.services import ai_tools
from lifeline.services.ai_tool_schemas import TOOLS
from lifeline.services.ai_tools import RISK_LEVELS, ToolError

_CONVERSATIONS: dict = {}
_PENDING_ACTIONS: dict = {}

SYSTEM_PROMPT = """You are the built-in Business Assistant for LIFELINE, a point-of-sale app used by \
small independent shop owners who are often not very technical. Be warm, extremely concise, and use \
plain everyday language — never accounting or engineering jargon.

Rules you must always follow:
- Never silently record a sale, refund, price change, discount, inventory adjustment, or expense.
  Always call calculate_cart (or the relevant lookup) first, present a clear summary with the total,
  and wait for the user to explicitly confirm before the high/medium risk tool actually runs.
- If a product name is ambiguous (matches more than one product), list the options and ask which one.
- If a price is missing for a manual item, ask what price to record.
- If requested quantity exceeds recorded stock, tell the user and ask whether to continue anyway.
- When answering business questions, always state which time period the numbers cover.
- Clearly separate: things you looked up (facts), things you calculated (math on those facts), and
  any recommendation or prediction you're making (label it as your suggestion, not a fact).
- If a tool call fails because the user lacks permission, tell them plainly they don't have access to that.
- Keep replies short — this is a busy shop counter, not a report.
"""

_NUMBER_WORDS = {
    "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}

_SALE_TRIGGER = re.compile(r"\b(sold|sell|selling)\b", re.IGNORECASE)
_ITEM_SPLIT = re.compile(r",| and ", re.IGNORECASE)
_FILLER_WORDS = {"i", "a", "an", "the", "of", "some", "to", "me", "customer", "bought", "for", "paid"}
_UNIT_WORDS = {"packets", "packet", "pieces", "piece", "bottles", "bottle", "loaves", "loaf", "litres", "litre", "liters", "liter", "kgs", "kg", "units", "unit"}

def _get_history(conversation_id: str) -> list:
    return _CONVERSATIONS.setdefault(conversation_id, [])

def _summarize_tool_call(tool_name: str, arguments: dict) -> str:
    if tool_name == "create_sale":
        items = arguments.get("items", [])
        lines = [f"{i.get('quantity')} × {i.get('product_name') or i.get('product_id')}" for i in items]
        payments = arguments.get("payments", [])
        pay_lines = [f"{p.get('amount')} via {p.get('method')}" for p in payments]
        return "Record sale: " + ", ".join(lines) + " — Payment: " + ", ".join(pay_lines)
    if tool_name == "create_return":
        return f"Process a return on sale {arguments.get('sale_id')}: {arguments.get('reason')}"
    if tool_name == "adjust_inventory":
        return f"Adjust stock for {arguments.get('product_query')} by {arguments.get('quantity_changed')} ({arguments.get('reason')})"
    if tool_name == "create_expense":
        return f"Record expense: {arguments.get('category')} — {arguments.get('amount')}"
    if tool_name == "create_customer":
        return f"Create new customer: {arguments.get('name')}"
    return f"{tool_name}({json.dumps(arguments)})"
def _execute_tool(db: Session, user, tool_name: str, arguments: dict) -> dict:
    func = ai_tools.TOOL_FUNCTIONS.get(tool_name)
    if not func:
        raise ToolError(f"Unknown tool: {tool_name}")
    return func(db, user, **arguments)

def _run_with_gemini(db: Session, user, msg_in: AssistantMessageIn, conversation_id: str) -> AssistantMessageOut:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    history = _get_history(conversation_id)
    history.append(types.Content(role="user", parts=[types.Part.from_text(text=msg_in.message)]))

    proposed_action: Optional[ProposedAction] = None
    final_text = ""
    gemini_tools = [types.Tool(function_declarations=TOOLS)]

    for _ in range(6):
        combined_prompt = SYSTEM_PROMPT + f"\nThe logged-in user's role is {user.role}. Their permissions: {sorted(user.effective_permissions())}."
        config = types.GenerateContentConfig(
            system_instruction=combined_prompt,
            tools=gemini_tools,
            temperature=0.2
        )

        response = client.models.generate_content(
            model=settings.AI_MODEL,
            contents=history,
            config=config,
        )

        if response.candidates and response.candidates[0].content:
            history.append(response.candidates[0].content)
        if response.text:
            final_text += response.text

        function_calls = response.function_calls
        if not function_calls:
            break

        risky_call = next((fc for fc in function_calls if RISK_LEVELS.get(fc.name) in ("medium", "high")), None)
        if risky_call:
            action_id = str(uuid.uuid4())
            args_dict = risky_call.args if isinstance(risky_call.args, dict) else dict(risky_call.args)
            proposed_action = ProposedAction(
                action_id=action_id,
                tool_name=risky_call.name,
                risk_level=RISK_LEVELS.get(risky_call.name, "high"),
                arguments=args_dict,
                summary=_summarize_tool_call(risky_call.name, args_dict),
            )
            _PENDING_ACTIONS[action_id] = {
                "conversation_id": conversation_id,
                "tool_name": risky_call.name,
                "arguments": args_dict,
            }
            break

        function_responses = []
        for fc in function_calls:
            args_dict = fc.args if isinstance(fc.args, dict) else dict(fc.args)
            try:
                result = _execute_tool(db, user, fc.name, args_dict)
                content = result
            except ToolError as e:
                content = {"error": str(e)}
            except Exception as e:
                content = {"error": f"Something went wrong: {e}"}
            function_responses.append(
                types.Part.from_function_response(
                    name=fc.name,
                    response={"result": content}
                )
            )

        history.append(types.Content(role="user", parts=function_responses))

    return AssistantMessageOut(
        conversation_id=conversation_id,
        reply_text=final_text or "Okay.",
        speak_text=final_text[:220] if final_text else None,
        proposed_action=proposed_action,
    )

def _parse_quantity(token: str) -> Optional[int]:
    token = token.strip().lower()
    if token.isdigit():
        return int(token)
    return _NUMBER_WORDS.get(token)
def _extract_quantity_and_product(segment: str) -> Optional[tuple]:
    words = [w for w in re.findall(r"[a-zA-Z']+|\d+", segment)]
    quantity = None
    product_words = []
    for w in words:
        lw = w.lower()
        if lw in _FILLER_WORDS or lw in _UNIT_WORDS:
            continue
        if quantity is None:
            parsed = _parse_quantity(w)
            if parsed is not None:
                quantity = parsed
                continue
        product_words.append(w)

    if not product_words:
        return None
    return (quantity or 1, " ".join(product_words).strip())

def _rule_based_reply(db: Session, user, msg_in: AssistantMessageIn, conversation_id: str) -> AssistantMessageOut:
    text = msg_in.message.strip()
    lower = text.lower()

    if any(k in lower for k in ["how much have i made", "how are sales", "sales today", "what did we sell"]):
        summary = ai_tools.get_sales_summary(db, user, "today")
        reply = (
            f"{summary['period']}: sales KSh {summary['total_sales']:.0f} across "
            f"{summary['transaction_count']} transactions (avg KSh {summary['average_transaction']:.0f})."
        )
        return AssistantMessageOut(conversation_id=conversation_id, reply_text=reply, data=summary)

    if "low" in lower and "stock" in lower or "almost finished" in lower or "restock" in lower:
        result = ai_tools.get_low_stock_products(db, user)
        if not result["products"]:
            reply = "Nothing is low on stock right now."
        else:
            names = ", ".join(p["name"] for p in result["products"][:6])
            reply = f"Low on stock: {names}."
        return AssistantMessageOut(conversation_id=conversation_id, reply_text=reply, data=result)

    if _SALE_TRIGGER.search(lower):
        segments = [s.strip() for s in _ITEM_SPLIT.split(text) if s.strip()]
        cart_items = []
        for seg in segments:
            seg_clean = _SALE_TRIGGER.sub("", seg).strip().rstrip(".")
            parsed = _extract_quantity_and_product(seg_clean)
            if not parsed:
                continue
            qty, product_name = parsed
            if product_name:
                cart_items.append({"product_name": product_name, "quantity": qty})

        if not cart_items:
            return AssistantMessageOut(
                conversation_id=conversation_id,
                reply_text="I couldn't quite catch which products were sold — could you name them, e.g. '2 milk and 1 bread'?",
                requires_clarification=True,
            )

        cart = ai_tools.calculate_cart(db, user, cart_items)
        if cart["ambiguous"]:
            first = cart["ambiguous"][0]
            options_text = "\n".join(f"{i+1}. {o['name']} — KSh {o['price']:.0f}" for i, o in enumerate(first["options"]))
            return AssistantMessageOut(
                conversation_id=conversation_id,
                reply_text=f"Which {first['query']} did you mean?\n{options_text}",
                requires_clarification=True,
                clarification_options=first["options"],
            )
        if cart["not_found"]:
            return AssistantMessageOut(
                conversation_id=conversation_id,
                reply_text=f"I couldn't find a product called '{cart['not_found']}'. Could you check the name?",
                requires_clarification=True,
            )

        lines = "\n".join(f"{i['quantity']} × {i['name']} — KSh {i['line_total']:.0f}" for i in cart["resolved_items"])
        action_id = str(uuid.uuid4())
        arguments = {
            "items": [
                {"product_id": i["product_id"], "quantity": i["quantity"], "unit_price": i["unit_price"]}
                for i in cart["resolved_items"]
            ],
            "payments": [{"method": "cash", "amount": cart["total"]}],
        }
        _PENDING_ACTIONS[action_id] = {"conversation_id": conversation_id, "tool_name": "create_sale", "arguments": arguments}
        proposed = ProposedAction(
            action_id=action_id, tool_name="create_sale", risk_level="high",
            arguments=arguments, summary=f"Record sale totalling KSh {cart['total']:.0f}",
        )
        return AssistantMessageOut(
            conversation_id=conversation_id,
            reply_text=f"I found:\n{lines}\n\nTotal: KSh {cart['total']:.0f}\n\nHow did the customer pay? (I'll default to cash unless you tell me otherwise.) Record this sale?",
            proposed_action=proposed,
            data=cart,
        )

    return AssistantMessageOut(
        conversation_id=conversation_id,
        reply_text=(
            "I can help you record sales, check stock, or answer questions like 'how much have I made today?'. "
            "Connect an AI provider in Settings for full natural-language support."
        ),
    )

def process_message(db: Session, user, msg_in: AssistantMessageIn) -> AssistantMessageOut:
    conversation_id = msg_in.conversation_id or str(uuid.uuid4())

    if msg_in.confirm_action_id:
        pending = _PENDING_ACTIONS.pop(msg_in.confirm_action_id, None)
        if not pending:
            return AssistantMessageOut(
                conversation_id=conversation_id,
                reply_text="That action isn't waiting for confirmation anymore — nothing was changed.",
            )
        if not msg_in.confirmed:
            return AssistantMessageOut(conversation_id=conversation_id, reply_text="Okay, cancelled. Nothing was recorded.")
        try:
            result = _execute_tool(db, user, pending["tool_name"], pending["arguments"])
        except ToolError as e:
            return AssistantMessageOut(conversation_id=conversation_id, reply_text=str(e))
        except Exception as e:
            return AssistantMessageOut(conversation_id=conversation_id, reply_text=f"Something went wrong: {e}")

        if pending["tool_name"] == "create_sale":
            reply = f"Done — receipt {result['receipt_number']}, total KSh {result['total_amount']:.0f}."
        else:
            reply = f"Done. {json.dumps(result)}"
        return AssistantMessageOut(conversation_id=conversation_id, reply_text=reply, data=result)

    if settings.AI_PROVIDER == "google" and settings.GEMINI_API_KEY:
        try:
            return _run_with_gemini(db, user, msg_in, conversation_id)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return _rule_based_reply(db, user, msg_in, conversation_id)