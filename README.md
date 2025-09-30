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

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure your `.env` file contains:
```
ANTHROPIC_API_KEY=your_api_key_here
```

## Usage

Run the test chatbot:
```bash
cd WaiterAI
python test_chatbot.py
```

### Test Commands

- `quit` or `exit` - End the conversation
- `history` - View complete chat history
- `orders` - View all placed orders
- `clear` - Clear chat history and start fresh

### Example Conversations

```
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
