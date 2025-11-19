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

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal

# Example schemas (you can keep these for reference)

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

# --------------------------------------------------
# CRM: Client schema (collection name: "client")

class Address(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

class ContactPreferences(BaseModel):
    preferred_channel: Optional[Literal["email", "phone", "sms", "whatsapp", "none"]] = "email"
    allow_marketing: bool = True
    best_time: Optional[Literal["morning", "afternoon", "evening"]] = None

class Client(BaseModel):
    """Basic CRM client record"""
    first_name: str = Field(..., description="Client first name")
    last_name: str = Field(..., description="Client last name")
    email: Optional[EmailStr] = Field(None, description="Primary email")
    phone: Optional[str] = Field(None, description="Primary phone number")
    company: Optional[str] = Field(None, description="Company name")
    address: Optional[Address] = None
    tags: List[str] = Field(default_factory=list, description="Free-form tags")
    notes: Optional[str] = None
    newsletter_subscribed: bool = Field(default=True)
    contact_preferences: Optional[ContactPreferences] = None
    lead_status: Optional[Literal["lead", "customer", "prospect", "inactive"]] = "lead"
