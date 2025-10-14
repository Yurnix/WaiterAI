from sqlalchemy.orm import joinedload, selectinload
from db_connection import get_session
from db_models import Base, MenuCategory, Offering, Ingredient, Attribute, OfferingIngredient, OrderItem, OrderItemModification, faq
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, selectinload, joinedload
from typing import Optional, List




def getCategories(is_food: bool = None) -> dict:
    with get_session() as session:
        query = session.query(MenuCategory.name)
        if is_food is not None:
            query = query.filter(MenuCategory.is_food == is_food)
        categories = [name for name, in query.all()]
        return {"categories": categories}

def getMenu(
    is_food: bool = None, 
    category: list[str] = None, 
    is_recommended: bool = None,
    min_price: float = None,
    max_price: float = None,
    must_include: list[str] = None, 
    must_exclude: list[str] = None
) -> dict:
    """
    Retrieves a structured menu based on specified filters.

    Args:
        is_food: Optional. Filter for food (True) or drinks (False).
        category: Optional. A list of category names to include.
        is_recommended: Optional. Filter for items marked as recommended (True) or not (False).
        min_price: Optional. The minimum price for an item.
        max_price: Optional. The maximum price for an item.
        must_include: Optional. A list of ingredient names that must be in the offerings.
        must_exclude: Optional. A list of ingredient names that must not be in the offerings.
        
    Returns:
        A dictionary containing a list of menu items that match the filters.
    """
    with get_session() as session:
        query = session.query(Offering).options(
            joinedload(Offering.category),
            selectinload(Offering.ingredients).joinedload(OfferingIngredient.ingredient).selectinload(Ingredient.attributes)
        )

        # Apply filters based on the provided arguments
        if is_food is not None:
            query = query.join(Offering.category).filter(MenuCategory.is_food == is_food)
        
        if category:
            query = query.join(Offering.category).filter(MenuCategory.name.in_(category))
        
        if is_recommended is not None:
            query = query.filter(Offering.recommended == is_recommended)

        # --- ADDED PRICE RANGE FILTER ---
        if min_price is not None:
            query = query.filter(Offering.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Offering.price <= max_price)
        # --- END ADDED ---
            
        if must_include:
            for ingredient_name in must_include:
                query = query.filter(Offering.ingredients.any(
                    OfferingIngredient.ingredient.has(Ingredient.name == ingredient_name)
                ))

        if must_exclude:
            for ingredient_name in must_exclude:
                query = query.filter(~Offering.ingredients.any(
                    OfferingIngredient.ingredient.has(Ingredient.name == ingredient_name)
                ))

        offerings = query.all()

        result_items = []
        for item in offerings:
            all_attributes = {
                attr.attribute_name 
                for assoc in item.ingredients 
                for attr in assoc.ingredient.attributes
            }
            result_items.append({
                "category": item.category.name if item.category else "Uncategorized",
                "food": item.name,
                "price": float(item.price), # Added price to the output
                "description": item.description,
                "ingredients": [assoc.ingredient.name for assoc in item.ingredients],
                "excluded items": sorted(list(all_attributes))
            })
            
        return {"items": result_items}
def get_allergens(item_name: str, allergens_to_check: Optional[List[str]] = None) -> List[str]:
    """
    Retrieves potential allergens for a menu item based on its ingredients.

    Args:
        item_name: The exact name of the menu offering.
        allergens_to_check: An optional list of allergen names to specifically check for.

    Raises:
        ValueError: If the specified item_name does not exist in the database.

    Returns:
        If allergens_to_check is None, it returns a list of all allergen names 
        associated with the item (e.g., ['Gluten', 'Dairy', 'Pork']).
        
        If allergens_to_check is provided, it returns a list of formatted strings
        (e.g., ['Lasagne alla Bolognese contains Gluten', 'Lasagne alla Bolognese does not contain Nuts']).
    """
    with get_session() as session:
        # Step 1: Find the offering to ensure it exists.
        offering = session.query(Offering).filter(Offering.name == item_name).first()
        if not offering:
            raise ValueError(f"Offering '{item_name}' not found.")

        # Step 2: Construct a query to find all unique attributes (allergens)
        # linked to the ingredients of the specified offering.
        allergen_query = session.query(Attribute.attribute_name).join(
            Attribute.ingredients
        ).join(
            Ingredient.offerings
        ).filter(
            OfferingIngredient.offering_id == offering.offering_id
        ).distinct()

        # The query returns a list of tuples, so we flatten it into a simple list.
        # e.g., [('Gluten',), ('Dairy',)] becomes ['Gluten', 'Dairy']
        actual_allergens = [name for name, in allergen_query.all()]

        # --- Mode 1: Return all allergens for the item ---
        if allergens_to_check is None:
            return actual_allergens

        # --- Mode 2: Check for specific allergens ---
        else:
            results = []
            # Convert the list to a set for faster lookups (O(1) average time complexity)
            actual_allergens_set = set(actual_allergens)
            for allergen in allergens_to_check:
                if allergen in actual_allergens_set:
                    results.append(f"{offering.name} contains {allergen}")
                else:
                    results.append(f"{offering.name} does not contain {allergen}")
            return results



def placeOrder(order_id: int, item_name: str, quantity: int, special_instructions: str = None, ingredients_to_exclude: list[str] = None) -> str:
    """
    Places an order for a specific item, checking for sufficient quantity and updating stock.

    Args:
        order_id: The ID of the parent order.
        item_name: The name of the offering to order.
        quantity: The number of items to order.
        special_instructions: Any special instructions for the kitchen.
        ingredients_to_exclude: A list of ingredient names to remove from the offering.

    Returns:
        A success or failure message as a string.
    """
    ingredients_to_exclude = ingredients_to_exclude or []

    with get_session() as session:
        # 1. Find the offering in the database
        offering = session.query(Offering).filter(Offering.name == item_name).first()

        if not offering:
            raise ValueError(f"Offering '{item_name}' not found.")

        # 2. Check if the requested quantity is available in stock
        if offering.quantity < quantity:
            return f"Order cannot be placed as you requested {quantity} {offering.name} but only {offering.quantity} in stock"

        # 3. Create the new order item with the added details
        new_order_item = OrderItem(
            order_id=order_id,
            offering_id=offering.offering_id,
            quantity=quantity,
            special_instructions=special_instructions
        )
        session.add(new_order_item)

        # 4. Handle any ingredient modifications (same as before)
        for ingredient_name in ingredients_to_exclude:
            assoc = session.query(OfferingIngredient).join(Ingredient).filter(
                OfferingIngredient.offering_id == offering.offering_id,
                Ingredient.name == ingredient_name
            ).first()

            if not assoc:
                raise ValueError(f"'{ingredient_name}' is not an ingredient of '{item_name}'.")
            if not assoc.is_removable:
                raise ValueError(f"Ingredient '{ingredient_name}' cannot be removed from '{item_name}'.")

            modification = OrderItemModification(
                order_item=new_order_item,
                ingredient_id_to_remove=assoc.ingredient_id
            )
            session.add(modification)

        offering.quantity -= quantity

        session.commit()
        return f"Successfully placed order for {quantity} x '{item_name}' (Order Item ID: {new_order_item.order_item_id})."

def cancel_order_item(order_item_id: int) -> str:
    """
    Cancels an order item if its status is 'pending'.

    When an item is cancelled, its quantity is returned to the offering's stock.

    Args:
        order_item_id: The ID of the order item to cancel.

    Returns:
        A string with the success or failure message.
    """
    with get_session() as session:
        # Find the order item and lock the row to prevent race conditions
        order_item = session.query(OrderItem).filter(
            OrderItem.order_item_id == order_item_id
        ).with_for_update().first()

        if not order_item:
            raise ValueError(f"Order Item with ID {order_item_id} not found.")

        # 1. Check if the order status is 'pending'
        if order_item.order_status != 'pending':
            return f"Order item cannot be cancelled as its status is '{order_item.order_status}'."

        # 2. Add the quantity back to the offering's stock
        # The 'offering' relationship on the OrderItem model makes this easy
        order_item.offering.quantity += order_item.quantity

        # 3. Update the status to 'cancelled'
        order_item.order_status = 'cancelled'

        session.commit()
        return f"Order Item ID {order_item_id} has been successfully cancelled."
    

# This function depends on the placeOrder function from the previous example.
# from somewhere import placeOrder

def update_order_item_quantity(order_item_id: int, new_quantity: int) -> str:
    """
    Updates the quantity of an order item.

    - If the item's status is 'pending', it modifies the quantity directly and
      adjusts the stock accordingly.
    - If the status is not 'pending', it creates a new order item for the same order.
    - Setting new_quantity to 0 will cancel the item.

    Args:
        order_item_id: The ID of the order item to update.
        new_quantity: The desired new quantity for the item.

    Returns:
        A string with the success or failure message.
    """
    if new_quantity < 0:
        return "Quantity must be a non-negative number."

    # If the user wants to set the quantity to 0, we just cancel the item.
    if new_quantity == 0:
        return cancel_order_item(order_item_id)

    with get_session() as session:
        order_item = session.query(OrderItem).filter(
            OrderItem.order_item_id == order_item_id
        ).with_for_update().first()

        if not order_item:
            raise ValueError(f"Order Item with ID {order_item_id} not found.")

        # --- Behavior 1: Order status is 'pending' ---
        if order_item.order_status == 'pending':
            offering = order_item.offering
            quantity_difference = new_quantity - order_item.quantity

            # Check for stock only if we are INCREASING the quantity
            if quantity_difference > 0 and offering.quantity < quantity_difference:
                return f"Cannot increase quantity. Only {offering.quantity} additional items are in stock."

            # Adjust offering stock by the difference
            offering.quantity -= quantity_difference
            # Update the order item's quantity
            order_item.quantity = new_quantity

            session.commit()
            return f"Successfully updated quantity for item {order_item_id} to {new_quantity}."

        # --- Behavior 2: Order status is NOT 'pending' ---
        else:
            # The item is already being prepared or is served, so we create a new one.
            # This requires calling the previously defined placeOrder function.
            session.expunge(order_item) # Detach the old item from this session
            
            # NOTE: We are assuming `placeOrder` is available here.
            # We pass the original order's ID and the item's name to create a new, separate entry.
            return placeOrder(
                order_id=order_item.order_id,
                item_name=order_item.offering.name,
                quantity=new_quantity
            )


def receipt(order_id: int, item_names: list[str] = None) -> dict:
    with get_session() as session:
        query = session.query(OrderItem).options(
            joinedload(OrderItem.offering)
        ).filter(OrderItem.order_id == order_id)
        
        if item_names:
            query = query.join(Offering).filter(Offering.name.in_(item_names))
            
        order_items = query.all()
        
        receipt_items = [
            {"item name": item.offering.name, "item value": float(item.offering.price)}
            for item in order_items
        ]
        
        total = sum(item.offering.price for item in order_items)
        
        return {"items": receipt_items, "total": float(total)}

def payment(order_id: int, item_names: list[str] = None) -> str:
    with get_session() as session:
        query = session.query(OrderItem).filter(OrderItem.order_id == order_id)
        
        if item_names:
            query = query.join(Offering).filter(Offering.name.in_(item_names))

        order_items_to_update = query.with_for_update().all()
        
        if not order_items_to_update:
            return "No items found for the given criteria."
            
        count = 0
        for item in order_items_to_update:
            if item.order_status != 'paid':
                item.order_status = 'paid'
                count += 1
        
        if count > 0:
            return f"Payment successful. {count} item(s) marked as paid."
        else:
            return "All specified items were already paid."
        

def get_all_keys(session):
    #Retrieves all keys from the FAQ table. Returns a list of all key strings.
    with get_session() as session:
        session.query(faq.keys)
        keys_query = session.query(faq.key).all()
        return [key for key, in keys_query]


def get_value_for_key(session, key_to_find: str) -> str:
    #Retrieves the value for a specific key from the FAQ table.
    with get_session() as session:
        # Query for the first FAQ object that matches the key
        result = session.query(faq).filter_by(key=key_to_find).first()
        if result:
            return result.value
        return None
