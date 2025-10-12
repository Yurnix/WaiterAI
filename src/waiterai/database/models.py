from sqlalchemy import (
    Column, Integer, String, Text, DECIMAL, Boolean, Enum, TIMESTAMP, 
    ForeignKey, Table, UniqueConstraint
)
from sqlalchemy.orm import (relationship, DeclarativeBase)
from sqlalchemy.sql import func
from .connection import Base



# --- Association Table for Ingredient <-> Attribute ---
ingredient_attribute_association = Table('ingredient_attributes', Base.metadata,
    Column('ingredient_id', Integer, ForeignKey('ingredients.ingredient_id', ondelete='CASCADE'), primary_key=True),
    Column('attribute_id', Integer, ForeignKey('attributes.attribute_id', ondelete='CASCADE'), primary_key=True)
)

# --- Menu Models ---

class MenuCategory(Base):
    __tablename__ = 'menu_categories'
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    is_food = Column(Boolean, server_default='1')
    
    offerings = relationship("Offering", back_populates="category")

class Offering(Base):
    __tablename__ = 'offerings'
    offering_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    category_id = Column(Integer, ForeignKey('menu_categories.category_id', ondelete='SET NULL'))
    recommended = Column(Boolean, nullable=False, default=False)
    quantity = Column(Integer, nullable=False, default=0)
    category = relationship("MenuCategory", back_populates="offerings")
    ingredients = relationship("OfferingIngredient", back_populates="offering", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="offering")

# --- Ingredient Models (Normalized) ---

class Ingredient(Base):
    """Master table for unique ingredients (e.g., 'Tomato', 'Beef')."""
    __tablename__ = 'ingredients'
    ingredient_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)

    attributes = relationship("Attribute", secondary=ingredient_attribute_association, back_populates="ingredients")
    offerings = relationship("OfferingIngredient", back_populates="ingredient")
    modifications = relationship("OrderItemModification", back_populates="ingredient_to_remove")

class OfferingIngredient(Base):
    """
    This table links Offerings to Ingredients and holds the critical 
    'is_removable' flag specific to that combination.
    """
    __tablename__ = 'offering_ingredients'
    offering_id = Column(Integer, ForeignKey('offerings.offering_id', ondelete='CASCADE'), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey('ingredients.ingredient_id', ondelete='CASCADE'), primary_key=True)
    is_removable = Column(Boolean, server_default='1')
    
    offering = relationship("Offering", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="offerings")

class Attribute(Base):
    __tablename__ = 'attributes'
    attribute_id = Column(Integer, primary_key=True, autoincrement=True)
    attribute_name = Column(String(100), nullable=False, unique=True)

    ingredients = relationship("Ingredient", secondary=ingredient_attribute_association, back_populates="attributes")

# --- Ordering Models ---

class OrderItem(Base):
    __tablename__ = 'order_items'
    order_item_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, nullable=False, index=True)
    offering_id = Column(Integer, ForeignKey('offerings.offering_id'), nullable=False)
    special_instructions = Column(Text)
    order_status = Column(Enum('pending', 'preparing', 'served', 'paid', 'cancelled'), server_default='pending')
    sys_creation_date = Column(TIMESTAMP, server_default=func.now())
    sys_update_date = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    quantity = Column(Integer, nullable=False, default=1)
    offering = relationship("Offering", back_populates="order_items")
    modifications = relationship("OrderItemModification", back_populates="order_item", cascade="all, delete-orphan")

class OrderItemModification(Base):
    __tablename__ = 'order_item_modifications'
    modification_id = Column(Integer, primary_key=True, autoincrement=True)
    order_item_id = Column(Integer, ForeignKey('order_items.order_item_id', ondelete='CASCADE'), nullable=False)
    ingredient_id_to_remove = Column(Integer, ForeignKey('ingredients.ingredient_id', ondelete='RESTRICT'), nullable=False)

    order_item = relationship("OrderItem", back_populates="modifications")
    ingredient_to_remove = relationship("Ingredient", back_populates="modifications")


class FAQ(Base):
    __tablename__ = 'faq'
    key = Column(String(255), primary_key=True, nullable=False)
    value = Column(Text, nullable=False)