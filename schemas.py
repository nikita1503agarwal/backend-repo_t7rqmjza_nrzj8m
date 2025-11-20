"""
Database Schemas for Katalyst Apparels

Each Pydantic model represents a collection in MongoDB.
Collection name = lowercase of class name.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr

class Product(BaseModel):
    """
    Football Jersey products
    Collection: "product"
    """
    title: str = Field(..., description="Display name e.g. 'Arsenal Home Jersey 24/25'")
    team: str = Field(..., description="Team/Club name")
    league: Optional[str] = Field(None, description="League name")
    season: Optional[str] = Field(None, description="Season e.g. 24/25")
    description: Optional[str] = Field(None, description="Long description")
    price: float = Field(..., ge=0, description="Price in USD")
    currency: str = Field("USD", description="Currency code")
    sizes: List[str] = Field(default_factory=lambda: ["S", "M", "L", "XL"], description="Available sizes")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    in_stock: bool = Field(True, description="Whether in stock")
    stock_qty: Optional[int] = Field(None, ge=0, description="Quantity in stock if tracked")
    is_featured: bool = Field(False, description="Show on homepage hero")
    tags: List[str] = Field(default_factory=list, description="Search tags")
    colorway: Optional[str] = Field(None, description="Primary colorway")

class Customer(BaseModel):
    """Customers collection"""
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None

class OrderItem(BaseModel):
    product_id: str
    title: str
    price: float
    size: Optional[str] = None
    quantity: int = Field(1, ge=1)
    image: Optional[str] = None

class Order(BaseModel):
    """Orders collection"""
    customer_email: EmailStr
    items: List[OrderItem]
    total: float = Field(..., ge=0)
    currency: str = Field("USD")
    status: str = Field("pending", description="pending|paid|shipped|cancelled|refunded")
    notes: Optional[str] = None
