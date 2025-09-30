"""
MenuComponent - Handles menu-related operations for the restaurant chatbot.
This component follows Single Responsibility Principle - only deals with menu data.
"""
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MenuComponent:
    """
    Component responsible for managing menu information.
    In a real implementation, this would query a database or menu management system.
    """
    
    def __init__(self):
        """Initialize the menu component with dummy menu data."""
        # Dummy menu data for testing
        self.categories = ["Appetizers", "Main Course", "Desserts", "Beverages"]
        
        self.allergens = ["Peanuts", "Gluten", "Dairy", "Shellfish", "Soy", "Eggs"]
        
        self.menu_items = {
            "Appetizers": [
                {"name": "Caesar Salad", "price": 8.99, "allergens": ["Gluten", "Dairy", "Eggs"]},
                {"name": "Garlic Bread", "price": 5.99, "allergens": ["Gluten", "Dairy"]},
                {"name": "Spring Rolls", "price": 6.99, "allergens": ["Gluten", "Soy"]},
            ],
            "Main Course": [
                {"name": "Grilled Chicken", "price": 15.99, "allergens": []},
                {"name": "Pasta Carbonara", "price": 14.99, "allergens": ["Gluten", "Dairy", "Eggs"]},
                {"name": "Vegetable Stir Fry", "price": 12.99, "allergens": ["Soy"]},
                {"name": "Shrimp Scampi", "price": 18.99, "allergens": ["Shellfish", "Gluten", "Dairy"]},
            ],
            "Desserts": [
                {"name": "Chocolate Cake", "price": 6.99, "allergens": ["Gluten", "Dairy", "Eggs"]},
                {"name": "Ice Cream", "price": 4.99, "allergens": ["Dairy", "Eggs"]},
                {"name": "Fruit Salad", "price": 5.99, "allergens": []},
            ],
            "Beverages": [
                {"name": "Coffee", "price": 2.99, "allergens": []},
                {"name": "Orange Juice", "price": 3.99, "allergens": []},
                {"name": "Milkshake", "price": 5.99, "allergens": ["Dairy"]},
            ],
        }
    
    def get_items(self, params: Dict[str, Any]) -> str:
        """
        Get menu items for a specific category, optionally excluding items with certain allergens.
        
        Args:
            params: Dictionary containing:
                - category (str): The menu category (mandatory)
                - exclude_allergens (List[str], optional): List of allergens to exclude
        
        Returns:
            str: Formatted string of menu items or error message
        """
        try:
            category = params.get('category')
            exclude_allergens = params.get('exclude_allergens', [])
            
            if not category:
                logger.error("No category provided")
                return "Error: Category is required"
            
            if category not in self.menu_items:
                logger.warning(f"Category '{category}' not found")
                return f"Error: Category '{category}' not found. Available categories: {', '.join(self.categories)}"
            
            items = self.menu_items[category]
            
            # Filter items based on excluded allergens
            if exclude_allergens:
                filtered_items = []
                for item in items:
                    # Check if item contains any of the excluded allergens
                    has_excluded_allergen = any(allergen in item['allergens'] for allergen in exclude_allergens)
                    if not has_excluded_allergen:
                        filtered_items.append(item)
                items = filtered_items
            
            # Format the result
            if not items:
                result = f"No items found in '{category}' category"
                if exclude_allergens:
                    result += f" without allergens: {', '.join(exclude_allergens)}"
            else:
                result = f"Items in '{category}' category:\n"
                for item in items:
                    allergen_info = f" (Contains: {', '.join(item['allergens'])})" if item['allergens'] else " (No allergens)"
                    result += f"- {item['name']}: ${item['price']:.2f}{allergen_info}\n"
            
            logger.info(f"Retrieved items for category '{category}' with exclude_allergens: {exclude_allergens}")
            return result.strip()
            
        except Exception as e:
            logger.error(f"Error retrieving menu items: {e}")
            return f"Error: {str(e)}"
    
    def get_categories(self, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Get all available menu categories.
        
        Args:
            params: No parameters required (can be None or empty dict)
        
        Returns:
            str: Formatted string of all categories
        """
        try:
            result = "Available menu categories:\n" + "\n".join(f"- {cat}" for cat in self.categories)
            logger.info("Retrieved all menu categories")
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving categories: {e}")
            return f"Error: {str(e)}"
    
    def get_allergens(self, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Get all possible allergens that might be present in menu items.
        
        Args:
            params: No parameters required (can be None or empty dict)
        
        Returns:
            str: Formatted string of all allergens
        """
        try:
            result = "Allergens we track:\n" + "\n".join(f"- {allergen}" for allergen in self.allergens)
            logger.info("Retrieved all allergen information")
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving allergens: {e}")
            return f"Error: {str(e)}"


# Example of how to add more menu-related methods:
# 
# def search_items_by_name(self, params: Dict[str, Any]) -> str:
#     """
#     Search for menu items by name (partial match).
#     
#     Args:
#         params: Dictionary containing:
#             - search_term (str): The term to search for
#     
#     Returns:
#         str: Formatted string of matching items
#     """
#     try:
#         search_term = params.get('search_term', '').lower()
#         results = []
#         
#         for category, items in self.menu_items.items():
#             for item in items:
#                 if search_term in item['name'].lower():
#                     results.append(f"{item['name']} ({category}): ${item['price']:.2f}")
#         
#         if not results:
#             return f"No items found matching '{search_term}'"
#         
#         return "Search results:\n" + "\n".join(f"- {r}" for r in results)
#         
#     except Exception as e:
#         logger.error(f"Error searching items: {e}")
#         return f"Error: {str(e)}"
# 
# 
# def get_item_details(self, params: Dict[str, Any]) -> str:
#     """
#     Get detailed information about a specific menu item.
#     
#     Args:
#         params: Dictionary containing:
#             - item_name (str): Name of the item
#     
#     Returns:
#         str: Detailed information about the item
#     """
#     try:
#         item_name = params.get('item_name')
#         # Implementation here
#         return "Item details..."
#     except Exception as e:
#         logger.error(f"Error getting item details: {e}")
#         return f"Error: {str(e)}"
