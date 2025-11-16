"""
AnthropicLLM - Main LLM class that handles interaction with Anthropic's Claude API.
This class follows Dependency Injection principle - components are injected via constructor.
"""
import logging
from typing import List, Dict, Any, Optional, Callable
from anthropic import Anthropic
from anthropic.types import ToolParam, MessageParam, TextBlock, ToolUseBlock
from . import tool_wrappers

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AnthropicLLM:
    """
    Main LLM class that manages conversations with Claude AI.
    Uses dependency injection for components to maintain loose coupling.
    """
    
    # System prompt for the restaurant chatbot
    SYSTEM_PROMPT = """You are a friendly and helpful restaurant assistant chatbot. 
Your role is to help customers with:
1. Browsing the menu and finding items that match their preferences
2. Answering questions about menu items, including allergen information
3. Taking orders for food and beverages
4. Managing orders (updating quantities, cancelling)
5. Providing receipts and processing payments
6. Answering frequently asked questions about the restaurant

You have access to comprehensive tools to:
- Get menu categories and view all available items
- Search the menu with advanced filters (food/drink type, categories, price range, ingredients, allergens, recommendations)
- Check allergen information for specific menu items
- Place orders for customers with special instructions
- Update order item quantities or cancel orders
- Generate receipts showing items and totals
- Process payments for orders
- Access FAQ information to answer common questions

Be polite, helpful, and informative. When customers ask about the menu, use the appropriate 
tools to fetch real-time information. When they want to order, use the order placement tool.
Don't make up information about the menu, if something is absent or not specified, say so.
Always confirm orders with the customer and provide order IDs for reference.

When customers ask about pricing, dietary restrictions, or want recommendations, use the get_menu 
tool with appropriate filters. For specific allergen questions, use the get_allergens tool.
For general questions about the restaurant, check the FAQ tools first."""
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
        """
        Initialize the Anthropic LLM.
        
        Args:
            api_key: Anthropic API key
            model: Claude model to use (default: claude-sonnet-4-5-20250929)
        """
        self.client = Anthropic(api_key=api_key)
        self.model = model
        
        # Map tool names to their corresponding wrapper functions from tool_wrappers.py
        self.tool_map: Dict[str, Callable] = {
            "get_categories": tool_wrappers.wrap_get_categories,
            "get_menu": tool_wrappers.wrap_get_menu,
            "get_allergens": tool_wrappers.wrap_get_allergens,
            "place_order": tool_wrappers.wrap_place_order,
            "cancel_order_item": tool_wrappers.wrap_cancel_order_item,
            "update_order_item_quantity": tool_wrappers.wrap_update_order_item_quantity,
            "get_receipt": tool_wrappers.wrap_receipt,
            "process_payment": tool_wrappers.wrap_payment,
            "get_faq_keys": tool_wrappers.wrap_get_all_keys,
            "get_faq_value": tool_wrappers.wrap_get_value_for_key,
        }
        
        # Define tools for Claude
        self.tools = self._define_tools()
        
        logger.info(f"AnthropicLLM initialized with model: {model}")
    
    def _define_tools(self) -> List[ToolParam]:
        """
        Define the tools available to the LLM.
        
        Returns:
            List of tool definitions in Anthropic's format
        """
        tools: List[ToolParam] = [
            {
                "name": "get_categories",
                "description": "Get all available menu categories, optionally filtered by food or drink type.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "is_food": {
                            "type": "boolean",
                            "description": "Filter for food categories (true) or drink categories (false). Omit to get all categories."
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_menu",
                "description": "Search and filter the menu with advanced criteria including food/drink type, categories, recommendations, price range, and ingredient requirements.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "is_food": {
                            "type": "boolean",
                            "description": "Filter for food items (true) or drinks (false). Omit to get both."
                        },
                        "category": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of category names to filter by (e.g., ['Appetizers', 'Main Course'])"
                        },
                        "is_recommended": {
                            "type": "boolean",
                            "description": "Filter for recommended items (true) or non-recommended (false). Omit for all."
                        },
                        "min_price": {
                            "type": "number",
                            "description": "Minimum price for items"
                        },
                        "max_price": {
                            "type": "number",
                            "description": "Maximum price for items"
                        },
                        "must_include": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of ingredient names that must be present in the item"
                        },
                        "must_exclude": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of ingredient names that must NOT be present in the item (allergens)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_allergens",
                "description": "Get allergen information for a specific menu item. Can return all allergens or check specific ones.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "item_name": {
                            "type": "string",
                            "description": "The exact name of the menu item"
                        },
                        "allergens_to_check": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of specific allergens to check for (e.g., ['Gluten', 'Dairy']). If omitted, returns all allergens in the item."
                        }
                    },
                    "required": ["item_name"]
                }
            },
            {
                "name": "place_order",
                "description": "Place an order for a specific menu item with optional special instructions and ingredient exclusions.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "integer",
                            "description": "The ID of the parent order"
                        },
                        "item_name": {
                            "type": "string",
                            "description": "Name of the menu item to order"
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "Number of items to order (default: 1)",
                            "default": 1
                        },
                        "special_instructions": {
                            "type": "string",
                            "description": "Any special instructions for the kitchen"
                        },
                        "ingredients_to_exclude": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of ingredient names to remove from the offering"
                        }
                    },
                    "required": ["order_id", "item_name"]
                }
            },
            {
                "name": "cancel_order_item",
                "description": "Cancel an order item if its status is 'pending'. The quantity is returned to stock.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "order_item_id": {
                            "type": "integer",
                            "description": "The ID of the order item to cancel"
                        }
                    },
                    "required": ["order_item_id"]
                }
            },
            {
                "name": "update_order_item_quantity",
                "description": "Update the quantity of an existing order item. If pending, modifies directly. If not pending, creates a new order. Setting quantity to 0 cancels the item.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "order_item_id": {
                            "type": "integer",
                            "description": "The ID of the order item to update"
                        },
                        "new_quantity": {
                            "type": "integer",
                            "description": "The new quantity for the order item (0 to cancel)"
                        }
                    },
                    "required": ["order_item_id", "new_quantity"]
                }
            },
            {
                "name": "get_receipt",
                "description": "Generate a receipt for an order, showing all items and the total cost. Can optionally filter by specific item names.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "integer",
                            "description": "The ID of the order to generate receipt for"
                        },
                        "item_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of item names to include in receipt. Omit to include all items."
                        }
                    },
                    "required": ["order_id"]
                }
            },
            {
                "name": "process_payment",
                "description": "Process payment for order items, marking them as paid. Can process all items or specific items by name.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "integer",
                            "description": "The ID of the order to process payment for"
                        },
                        "item_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of item names to pay for. Omit to pay for all items."
                        }
                    },
                    "required": ["order_id"]
                }
            },
            {
                "name": "get_faq_keys",
                "description": "Get all available FAQ topics/keys that customers can ask about.",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_faq_value",
                "description": "Get the answer to a specific FAQ question by its key.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": "The FAQ key/topic to get the answer for"
                        }
                    },
                    "required": ["key"]
                }
            }
        ]
        
        return tools
    
    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """
        Execute a tool and return its result.
        
        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool
        
        Returns:
            str: String representation of the tool result
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"TOOL EXECUTION: {tool_name}")
        logger.info(f"INPUT PARAMETERS: {tool_input}")
        
        if tool_name not in self.tool_map:
            error_msg = f"Unknown tool: {tool_name}"
            logger.error(error_msg)
            return error_msg
        
        try:
            # Execute the tool
            result = self.tool_map[tool_name](tool_input)
            
            logger.info(f"OUTPUT: {result}")
            logger.info(f"{'='*60}\n")
            
            # Convert result to string for Claude
            return str(result)
            
        except Exception as e:
            error_msg = f"Error executing {tool_name}: {str(e)}"
            logger.error(error_msg)
            logger.info(f"{'='*60}\n")
            return error_msg
    
    def query(self, user_message: str, chat_history: Optional[List[MessageParam]] = None) -> str:
        """
        Send a query to Claude and handle any tool uses in a loop until completion.
        
        This method implements the core conversation loop:
        1. Send user message with chat history to Claude
        2. If Claude wants to use tools, execute them and provide results back
        3. Repeat until Claude provides a final text response without tools
        
        Args:
            user_message: The user's message/query
            chat_history: Optional list of previous messages in the conversation
        
        Returns:
            str: Claude's final text response
        """
        if chat_history is None:
            chat_history = []
        
        # Add the new user message to history
        messages = chat_history + [{"role": "user", "content": user_message}]
        
        logger.info(f"\n{'#'*60}")
        logger.info(f"NEW USER QUERY: {user_message}")
        logger.info(f"{'#'*60}\n")
        
        # Loop until we get a response without tool use
        while True:
            # Query Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.SYSTEM_PROMPT,
                messages=messages,
                tools=self.tools
            )
            
            logger.info(f"Claude response stop_reason: {response.stop_reason}")
            
            # Check if Claude wants to use tools
            if response.stop_reason == "tool_use":
                # Add Claude's response to message history
                messages.append({"role": "assistant", "content": response.content})
                
                # Process all tool uses in this response
                tool_results = []
                for content_block in response.content:
                    if content_block.type == "tool_use":
                        # Execute the tool
                        tool_result = self._execute_tool(
                            content_block.name,
                            content_block.input
                        )
                        
                        # Prepare tool result for next API call
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": content_block.id,
                            "content": tool_result
                        })
                
                # Add tool results to messages and continue loop
                messages.append({"role": "user", "content": tool_results})
                
            else:
                # No more tool use - extract final text response
                final_response = ""
                for content_block in response.content:
                    if isinstance(content_block, TextBlock):
                        final_response += content_block.text
                
                logger.info(f"\n{'#'*60}")
                logger.info(f"FINAL RESPONSE: {final_response}")
                logger.info(f"{'#'*60}\n")
                
                return final_response


# Example of how to add more tools:
#
# 1. First, create a new component or add a method to an existing component:
#    In order_component.py:
#    def get_order_status(self, params: Dict[str, Any]) -> str:
#        """Get the status of an order by ID."""
#        order_id = params.get('order_id')
#        # Implementation...
#        return status_info
#
# 2. Add the tool to the tool_map in __init__:
#    self.tool_map["get_order_status"] = self.order_component.get_order_status
#
# 3. Add the tool definition in _define_tools:
#    {
#        "name": "get_order_status",
#        "description": "Get the current status of an order by its ID.",
#        "input_schema": {
#            "type": "object",
#            "properties": {
#                "order_id": {
#                    "type": "integer",
#                    "description": "The ID of the order to check"
#                }
#            },
#            "required": ["order_id"]
#        }
#    }
#
# That's it! The tool will now be available to Claude and automatically executed when needed.
