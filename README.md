# Day 2: Tool-Enabled AI Agent (Calculator, Web Search & Real-Time Context)

An agentic Python terminal assistant that extends the Day 1 chatbot with **Function Calling / Tool Use** and **Real-Time Environmental Context**.

In addition to conversational text generation, the Day 2 agent has autonomous access to:
1. **Switch-Statement Calculator** ([`calculator.py`](calculator.py)): Performs arithmetic calculations locally using Python's `match ... case` statement.
2. **Live Web Search** ([`web_search.py`](web_search.py)): Queries DuckDuckGo for live internet data, latest software versions, breaking news, and current events.
3. **Real-Time Date & Time Awareness**: Injects live system clock information into the reasoning context to accurately answer date and time queries.

---

## What's New in Day 2

| Feature | Day 1 | Day 2 |
|---|---|---|
| **Capabilities** | Text generation only | Text generation + Tool Execution + Real-time Context |
| **Tools** | None | • Calculator (`calculator.py`)<br>• Live Web Search (`web_search.py`) |
| **Tool Calling Protocol** | N/A | OpenAI-compatible function calling via Hugging Face API |
| **Agentic Loop** | Single-turn completion | Multi-turn reasoning & tool execution loop |
| **Date & Time Awareness** | None (static model cutoff) | Dynamic system prompt with real-time calendar date |
| **Commands** | `/reset`, `/exit` | `/tools`, `/reset`, `/exit` |

---

## Architecture & How It Works

```
                        +----------------------+
                        |         User         |
                        +----------------------+
                                   |
                                   | "What is the current React version?"
                                   v
                        +----------------------+
                        |   Day 2 AI Agent     |  <--- Real-Time Date Context
                        | (ibm-granite-4.2-3b) |       (e.g., Today is October 1, 2026)
                        +----------------------+
                               /        \
          Math Query          /          \          Live / Web Query
                             /            \
                            v              v
                  +---------------+  +------------------+
                  | calculator.py |  |  web_search.py   |
                  | (match/case)  |  |   (DuckDuckGo)   |
                  +---------------+  +------------------+
                            \              /
                             \            /
                              v          v
                        +----------------------+
                        | Verified Tool Result |
                        +----------------------+
                                   |
                                   v
                        +----------------------+
                        | Final Response       |
                        | Synthesized to User  |
                        +----------------------+
```

1. **User asks a question** (e.g., *"What is 125 * 8?"* or *"current react version"* or *"current date"*).
2. **AI selects the appropriate tool or context**:
   - **Math questions** $\rightarrow$ calls `calculate(operation='multiply', a=125, b=8)`.
   - **Real-time / web questions** $\rightarrow$ calls `web_search(query='current React version')`.
   - **Calendar / date questions** $\rightarrow$ resolves using dynamic system date context.
   - **General conversational queries** $\rightarrow$ answers directly without invoking tools.
3. **Local Tool Execution**: The chosen tool runs locally in Python and returns structured results.
4. **Tool Result Fed Back to AI**: The chatbot passes the output with `role: "tool"` back to the model.
5. **Final Answer Synthesized**: The AI formulates an accurate, grounded response for the user.

---

## Tool Details

### 1. Switch-Statement Calculator (`calculator.py`)

Implemented using Python 3.10+ switch statement (`match ... case`):

- **Supported operations**:
  - `add` (`+`, `plus`, `sum`)
  - `subtract` (`-`, `minus`, `diff`)
  - `multiply` (`*`, `times`, `product`)
  - `divide` (`/`, `division`) — includes division-by-zero protection
  - `power` (`**`, `^`, `pow`, `exponent`)
  - `modulo` (`%`, `mod`) — includes modulo-by-zero protection
- **Safe Type Conversion**: Automatically handles string, integer, and float inputs.
- **Standalone testable**: Run `python calculator.py` to run built-in test suites.

### 2. Live Web Search (`web_search.py`)

- **Engine**: Powered by `ddgs` (DuckDuckGo search), requiring **no paid API keys**.
- **Features**: Fetches real-time web results, extracts titles and summaries, and returns source URLs.
- **Standalone testable**: Run `python web_search.py` to test queries directly from the command line.

---

## Setup (Windows PowerShell)

### 1. Create and Activate Virtual Environment

```powershell
cd "Day 2"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Configure Credentials

Ensure `.env` exists in `Day 2` with your Hugging Face credentials:

```powershell
Copy-Item .env.example .env
```

Open `.env` and verify:
```dotenv
HF_TOKEN=hf_your_token_here
HF_MODEL=ibm-granite/granite-4.2-3b
```

---

## Running the Chatbot

Activate the virtual environment and start the agent:

```powershell
python chatbot.py
```

### Example Interactions

#### 1. Real-Time Date Awareness
```text
You: current date
Assistant: Today's date is Thursday, October 1, 2026.

You: yesterdays date
Assistant: Yesterday was Wednesday, September 30, 2026.
```

#### 2. Switch-Statement Calculator
```text
You: What is 125 * 8?

[TOOL CALL] Invoking 'calculate'
            Arguments: {"operation": "multiply", "a": 125, "b": 8}
[TOOL OUTPUT] Result: 1000

Assistant: 125 × 8 = 1,000.
```

#### 3. Live Web Search
```text
You: current react version

[TOOL CALL] Invoking 'web_search'
            Arguments: {"query": "current React version"}
[TOOL OUTPUT] Result:
[1] React Versions - React
Summary: The React docs at react.dev provide documentation for the latest version of React...
Source: https://react.dev/versions

Assistant: The latest (current) React version is React 19.3, released on September 9, 2026.
```

### Available Interactive Commands

- `/tools` - Display currently available tools, their descriptions, and parameter schemas.
- `/reset` - Clear the current conversation history and reinitialize the system prompt.
- `/exit`  - Terminate the chatbot session.

