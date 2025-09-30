"""
Quick test script to verify the chatbot components work correctly.
This is a non-interactive test that runs a few predefined queries.
"""
import os
from dotenv import load_dotenv
from anthropic_llm import AnthropicLLM
from order_component import OrderComponent
from menu_component import MenuComponent

# Load environment variables
load_dotenv()


def main():
    """Run a quick test of the chatbot functionality."""
    
    print("="*60)
    print("RESTAURANT CHATBOT - QUICK TEST")
    print("="*60)
    print()
    
    # Get API key from environment
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not found in .env file")
        return
    
    # Initialize components
    print("✓ Initializing components...")
    order_component = OrderComponent()
    menu_component = MenuComponent()
    
    # Initialize LLM
    print("✓ Initializing Anthropic LLM...")
    llm = AnthropicLLM(
        api_key=api_key,
        order_component=order_component,
        menu_component=menu_component
    )
    
    print("✓ Initialization complete!\n")
    
    # Test queries
    test_queries = [
        "What categories do you have?",
        "Show me main course items without dairy",
        "I'd like to order 2 Grilled Chicken with no salt"
    ]
    
    chat_history = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"TEST QUERY {i}: {query}")
        print(f"{'='*60}\n")
        
        try:
            response = llm.query(query, chat_history)
            print(f"RESPONSE:\n{response}\n")
            
            # Update chat history
            chat_history.append({"role": "user", "content": query})
            chat_history.append({"role": "assistant", "content": response})
            
        except Exception as e:
            print(f"❌ Error: {e}\n")
            return
    
    # Display final orders
    print(f"\n{'='*60}")
    print("FINAL ORDER STATUS:")
    print(f"{'='*60}\n")
    orders = order_component.get_all_orders()
    if orders:
        for order in orders:
            print(f"Order ID: {order['order_id']}")
            print(f"  Item: {order['item_name']}")
            print(f"  Quantity: {order['quantity']}")
            print(f"  Status: {order['status']}")
            if order['special_instructions']:
                print(f"  Special Instructions: {order['special_instructions']}")
            print()
    else:
        print("No orders placed.")
    
    print(f"{'='*60}")
    print("✓ All tests completed successfully!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
