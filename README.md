# Restaurant Chatbot with Anthropic Claude

A restaurant assistant chatbot powered by Anthropic's Claude AI with tool-calling capabilities.

### Components

1. **OrderComponent** (`order_component.py`)
   - Handles order placement and cancellation
   - Maintains order state (dummy implementation)
   - Single Responsibility: Only deals with order operations

2. **MenuComponent** (`menu_component.py`)
   - Manages menu information (categories, items, allergens)
   - Provides menu browsing with allergen filtering
   - Single Responsibility: Only deals with menu data

3. **AnthropicLLM** (`anthropic_llm.py`)
   - Main LLM integration class
   - Implements query loop with tool usage handling
   - Uses Dependency Injection for loose coupling
   - Automatically executes tools until conversation completes

### Features

- **Tool-Based Architecture**: The LLM can call tools to:
  - Browse menu categories and items
  - Filter items by allergens
  - Place and cancel orders
  - Get allergen information

## Architecture

### High-Level Flow

1. The Streamlit UI (`app.py`, launched via `start_app.py`) handles every user interaction, manages session state, and renders the multi-tab experience (chat, menu, cart, settings).
2. UI actions call directly into shared business logic within `src/queries.py`, which uses SQLAlchemy sessions from `src/connection.py` and models defined in `src/models.py` to talk to the relational database identified by `DATABASE_URL`.
3. The chat tab instantiates `AnthropicLLM` (`src/anthropic_llm.py`). Claude receives the running chat history plus a system prompt and, when needed, issues `tool_use` calls.
4. Tool invocations are routed through `src/tool_wrappers.py`, which adapt the JSON input into the same query functions used by the UI so both paths stay in sync.
5. Responses (tool outputs or final assistant messages) are fed back into the Streamlit session, keeping the conversation synchronized with the database.

### UI Layer (Streamlit)

- `start_app.py` loads `.env`, validates `DATABASE_URL`, then runs `streamlit run app.py` on localhost.
- `app.py` configures themes (`src/theme.apply_theme`), localization (`src/i18n.py`), and caches background services that periodically call `queries.refresh_order_statuses` so pending items advance automatically.
- Session state persists the visitor’s table number, order ID, messages, language, and theme, ensuring table-aware context is available to both the UI widgets and the LLM.

### LLM + Tooling

- `AnthropicLLM` wraps the Anthropic Messages API with a system prompt tailored for restaurant assistance.
- Available tools (get menu, place order, cancel order item, receipts, payments, FAQ lookup, etc.) are declared once and mapped to wrapper functions.
- When Claude requests a tool, the wrapper executes the corresponding query, stringifies the result, and passes it back so the model can continue reasoning with real data.

### Data & Background Services

- `src/connection.py` lazily loads the database URL, creates a pooled SQLAlchemy engine, and exposes `get_session()` for transaction-scoped work.
- ORM models in `src/models.py` mirror the schema created by `sqlData/createTables.sql` (menu categories, offerings, ingredients/allergens, order items, FAQ entries).
- All database reads/writes (menu filters, allergen checks, order management, payments, receipts) funnel through functions in `src/queries.py`, guaranteeing consistent business rules regardless of whether the request came from a UI control or an LLM tool.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Ensure your `.env` file contains:

```env
ANTHROPIC_API_KEY=your_api_key_here
```

## Usage

Run the test chatbot:

```bash
cd WaiterAI
python test_chatbot.py
```

### Run the UI on localhost (no Docker)

1. Install dependencies

```bash
pip install -r requirements.txt
```

1. Configure environment

Create a `.env` file in the project root with:

```env
DATABASE_URL=mysql+pymysql://user:pass@127.0.0.1:3306/waiterai?charset=utf8mb4
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

1. Start the app

```bash
python start_app.py           # Opens http://127.0.0.1:8501
python start_app.py --port 8502
```

This launcher works on macOS, Windows, and Linux. The app binds to localhost by default.

### Test Commands

- `quit` or `exit` - End the conversation
- `history` - View complete chat history
- `orders` - View all placed orders
- `clear` - Clear chat history and start fresh

### Example Conversations

```text
You: What categories do you have?
Assistant: [Uses get_categories tool and displays available categories]

You: Show me the main course items without dairy
Assistant: [Uses get_items tool with exclude_allergens parameter]

You: I'd like to order 2 Grilled Chicken
Assistant: [Uses place_order_item tool and confirms with order ID]

You: Cancel order 1
Assistant: [Uses cancel_order_item tool and confirms cancellation]
```

## Logging

The application provides detailed logging for:

- Tool executions (name, parameters, results)
- LLM responses and stop reasons
- User queries and final responses

Log format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
