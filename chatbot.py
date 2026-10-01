"""Day 2 Chatbot: Tool-Enabled Agent with Calculator and Live Web Search.

This chatbot extends the terminal assistant by adding multi-tool capabilities:
1. Arithmetic calculation via switch-case statement (`calculator.py`).
2. Real-time web search via DuckDuckGo (`web_search.py`).

The AI can choose between tools, execute them locally, and use the results to
formulate accurate and up-to-date responses.
"""

from datetime import datetime
import json
import os
import sys

from dotenv import load_dotenv
import requests

from calculator import CALCULATOR_TOOL, calculate
from web_search import WEB_SEARCH_TOOL, search_web

# Ensure UTF-8 output encoding across Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL = os.getenv("HF_MODEL", "ibm-granite/granite-4.2-3b")


def get_system_prompt() -> str:
    """Generate the system prompt with current date context and tool instructions."""
    now_str = datetime.now().strftime("%A, %B %d, %Y")
    return (
        "You are a helpful and intelligent AI assistant equipped with real-world tools.\n"
        f"Today's date is {now_str}.\n\n"
        "You have access to two tools:\n"
        "1. `calculate`: Performs arithmetic calculations (addition, subtraction, "
        "multiplication, division, power, modulo). Always call `calculate` whenever "
        "the user asks a mathematical calculation question.\n"
        "2. `web_search`: Searches the live web for up-to-date information, current news, "
        "recent events, software versions, weather, or real-time facts. Always call `web_search` whenever "
        "the user asks about current info, versions, recent developments, or external knowledge requiring verification.\n"
        "Always formulate your final answer based on the tool results returned or current date context. "
        "For general conversational questions that do not need calculation or live search, respond directly, clearly, and concisely."
    )


AVAILABLE_TOOLS = {
    "calculate": calculate,
    "web_search": search_web,
}
TOOLS = [CALCULATOR_TOOL, WEB_SEARCH_TOOL]


def call_completion_api(messages, token, tools=None):
    """Send a chat completion request to the Hugging Face Inference API."""
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 1536,
    }
    if tools:
        payload["tools"] = tools

    response = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]


def execute_agentic_turn(messages, token, max_tool_iterations=5):
    """Execute a turn with the LLM, resolving any tool calls in a loop.

    Returns:
        The final assistant response string.
    """
    iterations = 0

    while iterations < max_tool_iterations:
        iterations += 1
        message = call_completion_api(messages, token, tools=TOOLS)
        tool_calls = message.get("tool_calls")

        # If no tool calls were requested, the model has given its final response
        if not tool_calls:
            reply = message.get("content", "").strip()
            messages.append({"role": "assistant", "content": reply})
            return reply

        # The model requested one or more tool calls
        messages.append({
            "role": "assistant",
            "content": message.get("content") or "",
            "tool_calls": tool_calls,
        })

        for tool_call in tool_calls:
            call_id = tool_call.get("id")
            func_data = tool_call.get("function", {})
            func_name = func_data.get("name")
            raw_args = func_data.get("arguments", "{}")

            try:
                args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
            except json.JSONDecodeError:
                args = {}

            print(f"\n[TOOL CALL] Invoking '{func_name}'")
            print(f"            Arguments: {json.dumps(args)}")

            if func_name in AVAILABLE_TOOLS:
                try:
                    result = AVAILABLE_TOOLS[func_name](**args)
                except Exception as exc:
                    result = f"Error executing {func_name}: {exc}"
            else:
                result = f"Error: Tool '{func_name}' is not recognized."

            # Truncate preview if very long for clean terminal display
            preview = str(result)
            if len(preview) > 500:
                preview = preview[:500] + "... [truncated for display]"
            print(f"[TOOL OUTPUT] Result:\n{preview}\n")

            messages.append({
                "role": "tool",
                "tool_call_id": call_id,
                "name": func_name,
                "content": str(result),
            })

    # Fallback if tool iterations exceeded maximum
    fallback_msg = "Maximum tool call iterations reached without a final response."
    messages.append({"role": "assistant", "content": fallback_msg})
    return fallback_msg


def show_tools_info():
    """Print information about available tools."""
    print("\n--- Available Tools ---")
    print("1. calculate:")
    print("   Description: Evaluates arithmetic operations using a switch statement (match/case).")
    print("   Supported operations: add, subtract, multiply, divide, power, modulo.")
    print("   Parameters: operation (str), a (number), b (number)")
    print("2. web_search:")
    print("   Description: Searches the live web for current news, facts, recent events, and real-time info.")
    print("   Parameters: query (str)")
    print("------------------------\n")


def main():
    token = os.getenv("HF_TOKEN")
    if not token:
        print("Set HF_TOKEN in your .env file or environment variables.")
        print("Get a token at https://huggingface.co/settings/tokens")
        return

    system_prompt = get_system_prompt()
    messages = [{"role": "system", "content": system_prompt}]

    print("=" * 65)
    print("Day 2 Chatbot: Tool-Enabled Agent")
    print(f"Model: {MODEL}")
    print("Equipped with:")
    print("  • Switch-Statement Calculator Tool (calculator.py)")
    print("  • Live Web Search Tool (web_search.py via DuckDuckGo)")
    print("Commands:")
    print("  /tools - View available tools and capabilities")
    print("  /reset - Clear conversation history")
    print("  /exit  - Quit the chatbot")
    print("=" * 65 + "\n")

    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_text:
            continue

        if user_text.lower() in ("/exit", "exit", "quit", "/quit"):
            print("Goodbye!")
            break

        if user_text.lower() == "/reset":
            messages = [{"role": "system", "content": get_system_prompt()}]
            print("Conversation history cleared.\n")
            continue

        if user_text.lower() == "/tools":
            show_tools_info()
            continue

        messages.append({"role": "user", "content": user_text})

        # Save snapshot of index in case we need to roll back on failure
        added_user_idx = len(messages) - 1

        try:
            reply = execute_agentic_turn(messages, token)
        except requests.exceptions.HTTPError as error:
            # Roll back conversation history to before this turn
            del messages[added_user_idx:]
            detail = error.response.text if error.response is not None else str(error)
            print(f"\nHugging Face API returned an error: {detail}\n")
            continue
        except requests.exceptions.RequestException as error:
            del messages[added_user_idx:]
            print(f"\nNetwork error connecting to Hugging Face: {error}\n")
            continue
        except (KeyError, IndexError, TypeError, ValueError) as error:
            del messages[added_user_idx:]
            print(f"\nUnexpected response format encountered: {error}. Try again.\n")
            continue

        print(f"Assistant: {reply}\n")


if __name__ == "__main__":
    main()

