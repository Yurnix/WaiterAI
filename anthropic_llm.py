"""
AnthropicLLM - Main LLM class that handles interaction with Anthropic's Claude API.
This class follows Dependency Injection principle - components are injected via constructor.
"""
import logging
from typing import List, Dict, Any, Optional, Callable
from anthropic import Anthropic
from anthropic.types import ToolParam, MessageParam, TextBlock, ToolUseBlock

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
4. Cancelling orders if requested

You have access to tools to:
- Get menu categories and allergens
- Browse menu items by category, with optional allergen filtering
- Place orders for customers
- Cancel orders

Be polite, helpful, and informative. When customers ask about the menu, use the appropriate 
tools to fetch real-time information. When they want to order, use the order placement tool.
Don't make up information about the menu, if something is absent or not specified, say so.
Always confirm orders with the customer and provide order IDs for reference."""
    
    def __init__(self, api_key: str, order_component, menu_component, model: str = "claude-sonnet-4-5-20250929"):
        """
        Initialize the Anthropic LLM with injected components.
        
        Args:
            api_key: Anthropic API key
            order_component: Instance of OrderComponent for handling orders
            menu_component: Instance of MenuComponent for handling menu queries
            model: Claude model to use (default: claude-sonnet-4-5-20250929)
        """
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.order_component = order_component
        self.menu_component = menu_component
        
        # Map tool names to their corresponding methods
        # This follows Open/Closed Principle - easy to extend with new tools
        self.tool_map: Dict[str, Callable] = {
            "place_order_item": self.order_component.place_order_item,
            "cancel_order_item": self.order_component.cancel_order_item,
            "get_items": self.menu_component.get_items,
            "get_categories": self.menu_component.get_categories,
            "get_allergens": self.menu_component.get_allergens,
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
                "name": "place_order_item",
                "description": "Place an order for a menu item. Returns true if successful, false otherwise.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "item_name": {
                            "type": "string",
                            "description": "Name of the menu item to order"
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "Number of items to order",
                            "default": 1
                        },
                        "special_instructions": {
                            "type": "string",
                            "description": "Any special requests or modifications"
                        }
                    },
                    "required": ["item_name"]
                }
            },
            {
                "name": "cancel_order_item",
                "description": "Cancel a previously placed order. Returns true if successful, false otherwise.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "integer",
                            "description": "The ID of the order to cancel"
                        }
                    },
                    "required": ["order_id"]
                }
            },
            {
                "name": "get_items",
                "description": "Get menu items for a specific category, optionally filtering out items with certain allergens.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "The menu category to get items from (e.g., 'Appetizers', 'Main Course', 'Desserts', 'Beverages')"
                        },
                        "exclude_allergens": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of allergens to exclude (e.g., ['Gluten', 'Dairy'])"
                        }
                    },
                    "required": ["category"]
                }
            },
            {
                "name": "get_categories",
                "description": "Get all available menu categories. No parameters required.",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_allergens",
                "description": "Get list of all allergens tracked in the menu. No parameters required.",
                "input_schema": {
                    "type": "object",
                    "properties": {}
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
