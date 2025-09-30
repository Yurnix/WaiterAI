"""
OrderComponent - Handles order-related operations for the restaurant chatbot.
This component follows Single Responsibility Principle - only deals with orders.
"""
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrderComponent:
    """
    Component responsible for managing order operations.
    In a real implementation, this would interact with a database or order management system.
    """
    
    def __init__(self):
        """Initialize the order component with an empty order list."""
        self.orders = []  # Dummy storage for orders
        self.order_id_counter = 1
    
    def place_order_item(self, params: Dict[str, Any]) -> bool:
        """
        Place an order for a menu item.
        
        Args:
            params: Dictionary containing order details such as:
                - item_name (str): Name of the menu item
                - quantity (int): Number of items to order
                - special_instructions (str, optional): Any special requests
        
        Returns:
            bool: True if order was placed successfully, False otherwise
        """
        try:
            item_name = params.get('item_name', 'Unknown Item')
            quantity = params.get('quantity', 1)
            special_instructions = params.get('special_instructions', '')
            
            order = {
                'order_id': self.order_id_counter,
                'item_name': item_name,
                'quantity': quantity,
                'special_instructions': special_instructions,
                'status': 'placed'
            }
            
            self.orders.append(order)
            self.order_id_counter += 1
            
            logger.info(f"Order placed successfully: {order}")
            return True
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return False
    
    def cancel_order_item(self, params: Dict[str, Any]) -> bool:
        """
        Cancel a previously placed order.
        
        Args:
            params: Dictionary containing:
                - order_id (int): ID of the order to cancel
        
        Returns:
            bool: True if order was cancelled successfully, False otherwise
        """
        try:
            order_id = params.get('order_id')
            
            if order_id is None:
                logger.error("No order_id provided for cancellation")
                return False
            
            # Find and cancel the order
            for order in self.orders:
                if order['order_id'] == order_id:
                    order['status'] = 'cancelled'
                    logger.info(f"Order cancelled successfully: Order ID {order_id}")
                    return True
            
            logger.warning(f"Order ID {order_id} not found")
            return False
            
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return False
    
    def get_all_orders(self) -> list:
        """
        Get all orders (for testing/debugging purposes).
        
        Returns:
            list: List of all orders
        """
        return self.orders


# Example of how to add more order-related methods:
# 
# def update_order_item(self, params: Dict[str, Any]) -> bool:
#     """
#     Update an existing order.
#     
#     Args:
#         params: Dictionary containing:
#             - order_id (int): ID of the order to update
#             - new_quantity (int, optional): New quantity
#             - new_special_instructions (str, optional): Updated instructions
#     
#     Returns:
#         bool: True if order was updated successfully, False otherwise
#     """
#     try:
#         order_id = params.get('order_id')
#         # Implementation here
#         return True
#     except Exception as e:
#         logger.error(f"Error updating order: {e}")
#         return False
