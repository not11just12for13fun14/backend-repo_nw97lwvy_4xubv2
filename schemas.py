"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

# Example schemas (keep for reference):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Food Calories App Schemas

class MealType(str, Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"

class FoodItem(BaseModel):
    """
    A reusable food item with known calories per unit.
    Collection name: "fooditem"
    """
    name: str = Field(..., description="Food name")
    unit: str = Field("serving", description="Unit label, e.g., g, ml, piece, serving")
    calories_per_unit: float = Field(..., gt=0, description="Calories per unit")

class Entry(BaseModel):
    """
    A logged consumption entry for a specific day and meal.
    Collection name: "entry"
    """
    date: str = Field(..., description="Entry date in YYYY-MM-DD format")
    meal: MealType = Field(MealType.lunch, description="Meal type")
    name: str = Field(..., description="Food name (can be custom)")
    unit: str = Field("serving", description="Unit label")
    quantity: float = Field(1.0, gt=0, description="How many units consumed")
    calories_per_unit: float = Field(..., gt=0, description="Calories per single unit")
    notes: Optional[str] = Field(None, description="Optional notes")

# Note: The Flames database viewer can read these via GET /schema.
