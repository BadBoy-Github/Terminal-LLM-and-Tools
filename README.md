# Day 2: Tool-Enabled AI Agent with Switch-Statement Calculator

An agentic Python terminal assistant that extends the Day 1 chatbot with **Function Calling / Tool Use**. In addition to generating text, the AI has direct access to a local Python calculator (`calculator.py`) built using Python's switch statement (`match / case`).

When mathematical or calculation queries are received, the model automatically triggers a tool call to `calculate`, executes the function locally, and incorporates the verified numerical result into its final answer.

---

## What's New in Day 2

| Feature | Day 1 | Day 2 |
|---|---|---|
| **Capabilities** | Text generation only | Text generation + Tool Execution |
| **Tools** | None | Switch-statement calculator (`calculator.py`) |
| **Tool Calling Protocol** | N/A | OpenAI-compatible function calling via Hugging Face API |
| **Agentic Loop** | Single-turn completion | Multi-turn reasoning & tool execution loop |
| **Commands** | `/reset`, `/exit` | `/tools`, `/reset`, `/exit` |

---

## How It Works

1. **User asks a math question** (e.g., *"What is 75 multiplied by 8?"* or *"Calculate 2 to the power of 8"*).
2. **AI decides to call the tool**: The LLM determines that a calculation is required and outputs a `tool_calls` request with the function name `calculate` and arguments `{"operation": "multiply", "a": 75, "b": 8}`.
3. **Switch-statement calculator executes**: The `calculate` function in [`calculator.py`](calculator.py) matches the operation via Python's switch statement (`match op: case ...`) and performs the computation.
4. **Tool result sent back to AI**: The result (`600`) is returned to the model with role `"tool"`.
5. **Final response synthesized**: The model receives the verified tool output and crafts a clear response for the user.

```
+----------+      "What is 75 * 8?"      +------------+
|   User   | -------------------------> |  Day 2 AI  |
+----------+                            +------------+
     ^                                         |
     |                                         | Tool Call:
     | "75 multiplied by 8 is 600."            | calculate('multiply', 75, 8)
     |                                         v
+----------+      Result: 600           +-----------------+
| Response | <------------------------- |  calculator.py  |
+----------+                            |  (match / case) |
                                        +-----------------+
```

---

## Calculator Details (`calculator.py`)

The calculator is implemented using Python 3.10+ switch syntax (`match ... case`):

- **Supported operations**:
  - `add` (`+`, `plus`, `sum`)
  - `subtract` (`-`, `minus`, `diff`)
  - `multiply` (`*`, `times`, `product`)
  - `divide` (`/`, `division`) — includes division-by-zero protection
  - `power` (`**`, `^`, `pow`, `exponent`)
  - `modulo` (`%`, `mod`) — includes modulo-by-zero protection
- **Safe Type Conversion**: Automatically handles integer and float inputs.
- **Standalone testable**: Run `python calculator.py` to run built-in test cases.

---

## Setup (Windows PowerShell)

### 1. Create & Activate Virtual Environment

```powershell
cd "Day 2"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Configure API Credentials

Ensure `.env` exists in the `Day 2` directory with your Hugging Face credentials:

```powershell
Copy-Item .env.example .env
```

Open `.env` and verify:
```dotenv
HF_TOKEN=your_huggingface_token
HF_MODEL=ibm-granite/granite-4.2-3b
```

---

## Running the Chatbot

Activate the virtual environment and run:

```powershell
python chatbot.py
```

### Example Questions to Try

- **Multiplication**: `What is 75 multiplied by 8?`
- **Division**: `What is 144 divided by 12?`
- **Powers / Exponents**: `Calculate 2 to the power of 10.`
- **Modulo**: `What is 29 modulo 5?`
- **Non-math queries**: `What is the capital of France?` (Answers directly without invoking tools)

### Available Commands

- `/tools` - Inspect available tools, operations, and parameters.
- `/reset` - Clear the current conversation history.
- `/exit`  - Exit the chatbot.
