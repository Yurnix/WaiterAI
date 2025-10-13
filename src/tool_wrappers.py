"""
Tool wrappers for LLM integration with database queries.
These wrappers convert dict parameters from the LLM into function arguments for queries.py.
"""
from typing import Dict, Any, List
import queries


def wrap_get_categories(params: Dict[str, Any]) -> Dict:
    """Wrapper for queries.getCategories function."""
    return queries.getCategories(is_food=params.get('is_food'))


def wrap_get_menu(params: Dict[str, Any]) -> Dict:
    """Wrapper for queries.getMenu function."""
    return queries.getMenu(
        is_food=params.get('is_food'),
        category=params.get('category'),
        is_recommended=params.get('is_recommended'),
        min_price=params.get('min_price'),
        max_price=params.get('max_price'),
        must_include=params.get('must_include'),
        must_exclude=params.get('must_exclude')
    )


def wrap_get_allergens(params: Dict[str, Any]):
    """Wrapper for queries.get_allergens function."""
    return queries.get_allergens(
        item_name=params['item_name'],
        allergens_to_check=params.get('allergens_to_check')
    )


def wrap_place_order(params: Dict[str, Any]) -> str:
    """Wrapper for queries.placeOrder function."""
    return queries.placeOrder(
        order_id=params['order_id'],
        item_name=params['item_name'],
        quantity=params.get('quantity', 1),
        special_instructions=params.get('special_instructions'),
        ingredients_to_exclude=params.get('ingredients_to_exclude')
    )


def wrap_cancel_order_item(params: Dict[str, Any]) -> str:
    """Wrapper for queries.cancel_order_item function."""
    return queries.cancel_order_item(order_item_id=params['order_item_id'])


def wrap_update_order_item_quantity(params: Dict[str, Any]) -> str:
    """Wrapper for queries.update_order_item_quantity function."""
    return queries.update_order_item_quantity(
        order_item_id=params['order_item_id'],
        new_quantity=params['new_quantity']
    )


def wrap_receipt(params: Dict[str, Any]) -> Dict:
    """Wrapper for queries.receipt function."""
    return queries.receipt(
        order_id=params['order_id'],
        item_names=params.get('item_names')
    )


def wrap_payment(params: Dict[str, Any]) -> str:
    """Wrapper for queries.payment function."""
    return queries.payment(
        order_id=params['order_id'],
        item_names=params.get('item_names')
    )


def wrap_get_all_keys(params: Dict[str, Any]) -> List[str]:
    """Wrapper for queries.get_all_keys function."""
    return queries.get_all_keys(None)  # session parameter handled internally


def wrap_get_value_for_key(params: Dict[str, Any]) -> str:
    """Wrapper for queries.get_value_for_key function."""
    return queries.get_value_for_key(None, params['key'])  # session parameter handled internally
