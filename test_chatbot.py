"""
Test script for the restaurant chatbot using AnthropicLLM.
This script provides a terminal-based interface to chat with the AI assistant.
"""
import os
from dotenv import load_dotenv
from anthropic_llm import AnthropicLLM
from order_component import OrderComponent
from menu_component import MenuComponent
from anthropic.types import MessageParam
from typing import List

# Load environment variables
load_dotenv()


def print_separator(char='=', length=80):
    """Print a separator line."""
    print(char * length)


def print_welcome():
    """Print welcome message."""
    print_separator()
    print("🍽️  WELCOME TO THE RESTAURANT CHATBOT TEST 🍽️")
    print_separator()
    print("\nThis is a test interface for the restaurant assistant chatbot.")
    print("The bot can help you with:")
    print("  • Browse menu categories and items")
    print("  • Check allergen information")
    print("  • Place orders")
    print("  • Cancel orders")
    print("\nCommands:")
    print("  - Type 'quit' or 'exit' to end the conversation")
    print("  - Type 'history' to see all previous messages")
    print("  - Type 'orders' to see all placed orders")
    print("  - Type 'clear' to clear chat history and start fresh")
    print_separator()
    print()


def print_chat_history(messages: List[MessageParam]):
    """Print the chat history."""
    print_separator('-')
    print("CHAT HISTORY:")
    print_separator('-')
    
    if not messages:
        print("No messages yet.")
    else:
        for i, msg in enumerate(messages, 1):
            role = msg['role'].upper()
            content = msg['content']
            
            # Handle different content types
            if isinstance(content, str):
                print(f"\n[{i}] {role}:")
                print(content)
            elif isinstance(content, list):
                print(f"\n[{i}] {role}:")
                for item in content:
                    if isinstance(item, dict):
                        if item.get('type') == 'text':
                            print(item.get('text', ''))
                        elif item.get('type') == 'tool_result':
                            print(f"[Tool Result: {item.get('content', '')}]")
                    else:
                        print(item)
    
    print_separator('-')
    print()


def main():
    """Main function to run the chatbot test."""
    
    # Get API key from environment
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not found in .env file")
        return
    
    # Initialize components (Dependency Injection)
    print("Initializing components...")
    order_component = OrderComponent()
    menu_component = MenuComponent()
    
    # Initialize LLM
    print("Initializing Anthropic LLM...")
    llm = AnthropicLLM(
        api_key=api_key,
        order_component=order_component,
        menu_component=menu_component
    )
    
    print("✓ Initialization complete!\n")
    
    # Print welcome message
    print_welcome()
    
    # Chat history to maintain context
    chat_history: List[MessageParam] = []
    
    # Main conversation loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit']:
                print("\nThank you for testing the restaurant chatbot! Goodbye! 👋\n")
                break
            
            elif user_input.lower() == 'history':
                print_chat_history(chat_history)
                continue
            
            elif user_input.lower() == 'orders':
                print_separator('-')
                print("ALL ORDERS:")
                print_separator('-')
                orders = order_component.get_all_orders()
                if not orders:
                    print("No orders placed yet.")
                else:
                    for order in orders:
                        print(f"\nOrder ID: {order['order_id']}")
                        print(f"  Item: {order['item_name']}")
                        print(f"  Quantity: {order['quantity']}")
                        print(f"  Status: {order['status']}")
                        if order['special_instructions']:
                            print(f"  Special Instructions: {order['special_instructions']}")
                print_separator('-')
                print()
                continue
            
            elif user_input.lower() == 'clear':
                chat_history = []
                print("\n✓ Chat history cleared!\n")
                continue
            
            # Query the LLM
            print("\nAssistant: ", end='', flush=True)
            response = llm.query(user_input, chat_history)
            print(response)
            print()
            
            # Update chat history with the complete conversation
            # Add user message
            chat_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Add assistant response
            chat_history.append({
                "role": "assistant",
                "content": response
            })
            
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Exiting...")
            break
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'quit' to exit.\n")


if __name__ == "__main__":
    main()
