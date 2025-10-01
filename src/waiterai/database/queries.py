from sqlalchemy.orm import joinedload, selectinload
from .connection import get_session
from .models import Base, MenuCategory, Offering, Ingredient, Attribute, OfferingIngredient, OrderItem, OrderItemModification
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, selectinload, joinedload




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
    must_include: list[str] = None, 
    must_exclude: list[str] = None
) -> dict:
    with get_session() as session:
        query = session.query(Offering).options(
            joinedload(Offering.category),
            selectinload(Offering.ingredients).joinedload(OfferingIngredient.ingredient).selectinload(Ingredient.attributes)
        )

        if is_food is not None:
            query = query.join(Offering.category).filter(MenuCategory.is_food == is_food)
        
        if category:
            query = query.join(Offering.category).filter(MenuCategory.name.in_(category))
            
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
                "description": item.description,
                "ingredients": [assoc.ingredient.name for assoc in item.ingredients],
                "excluded items": sorted(list(all_attributes))
            })
            
        return {"items": result_items}

def placeOrder(order_id: int, item_name: str, ingredients_to_exclude: list[str] = None) -> str:
    ingredients_to_exclude = ingredients_to_exclude or []
        
    with get_session() as session:
        offering = session.query(Offering).filter(Offering.name == item_name).first()

        if not offering:
            raise ValueError(f"Offering '{item_name}' not found.")

        new_order_item = OrderItem(order_id=order_id, offering_id=offering.offering_id)
        session.add(new_order_item)
        
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
        
        session.flush()
        return f"Successfully placed order for '{item_name}' (Order Item ID: {new_order_item.order_item_id})."

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